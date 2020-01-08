from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_iam as iam
)


class ProxyStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = props['workspaces_vpc']

        # Proxy用のEIP
        eip = ec2.CfnEIP(self, 'EIP')
        eip_alloc_id = eip.attr_allocation_id

        # ユーザーデータ
        user_data = ec2.UserData.for_linux()
        user_data.add_commands('yum update -y')
        # EIPのアタッチを行う
        user_data.add_commands('eip_alloc_id={}'.format(eip_alloc_id))
        user_data.add_commands('instance_id=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)')
        user_data.add_commands('region=$(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone | sed -e "s/.$//")')
        user_data.add_commands('export AWS_DEFAULT_REGION=${region}')
        user_data.add_commands('aws ec2 associate-address --instance-id ${instance_id} --allocation-id ${eip_alloc_id}')
        # プロキシのインストールと設定を行う
        user_data.add_commands('yum install -y squid')
        user_data.add_commands("""cat <<EOF > /etc/squid/squid.conf
# Define local networks
acl localnet src 10.1.0.0/16

acl SSL_ports port 443
acl Safe_ports port 80		# http
acl Safe_ports port 443		# https
acl CONNECT method CONNECT

# Deny requests to certain unsafe ports
http_access deny !Safe_ports

# Deny CONNECT to other than secure SSL ports
http_access deny CONNECT !SSL_ports

# Only allow cachemgr access from localhost
http_access allow localhost manager
http_access deny manager

# We strongly recommend the following be uncommented to protect innocent
# web applications running on the proxy server who think the only
# one who can access services on "localhost" is a local user
http_access deny to_localhost

# Example rule allowing access from your local networks.
# Adapt localnet in the ACL section to list your (internal) IP networks
# from where browsing should be allowed
http_access allow localnet
http_access allow localhost

# include url white list 
acl whitelist dstdomain "/etc/squid/whitelist" 
http_access allow whitelist 

# And finally deny all other access to this proxy
http_access deny all

# Squid normally listens to port 3128
http_port 3128

# Leave coredumps in the first cache dir
coredump_dir /var/spool/squid
EOF""")
        user_data.add_commands('chmod 640 /etc/squid/squid.conf')
        user_data.add_commands('chgrp squid /etc/squid/squid.conf')
        user_data.add_commands("""cat <<EOF > /etc/squid/whitelist
# AWS Management Console
.aws.amazon.com
.amazonaws.com
.amazontrust.com
.cloudfront.net
.cloudfront.com
.sagemaker.aws
EOF""")
        user_data.add_commands('chmod 640 /etc/squid/whitelist')
        user_data.add_commands('chgrp squid /etc/squid/whitelist')
        user_data.add_commands('systemctl enable squid')
        user_data.add_commands('systemctl restart squid')

        # Proxy用AutoScalingGroup
        proxy_asg = autoscaling.AutoScalingGroup(
            self, 'ProxyAutoScalingGroup',
            instance_type=ec2.InstanceType('t2.small'),
            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
            key_name=self.node.try_get_context('key_name'),
            vpc=vpc,
            user_data=user_data,
            desired_capacity=1,
            max_capacity=1,
            min_capacity=1,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
        )

        # セキュリティーグループの設定
        proxy_asg.connections.allow_from_any_ipv4(
            ec2.Port.tcp(22)
        )

        # ユーザーデータからEIPをアタッチするために必要なポリシーをインスタンスロールにアタッチ
        proxy_asg.role.add_to_policy(
            statement=iam.PolicyStatement(
                actions=[
                    "ec2:AssociateAddress"
                ],
                resources=["*"]
            )
        )

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
