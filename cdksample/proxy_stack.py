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
        workspaces_workspaces_sg = props['workspaces_workspaces_sg']
        workspaces_endpoint_sg = props['workspaces_endpoint_sg']
        workspaces_hosted_zone = props['workspaces_hosted_zone']

        # ユーザーデータ
        user_data = ec2.UserData.for_linux()
        user_data.add_commands('yum update -y')

        # IPアドレスをRoute53に登録する
        user_data.add_commands('local_ip=$(curl -s http://169.254.169.254/latest/meta-data/local-ipv4)')
        user_data.add_commands('record=proxy.{}'.format(self.node.try_get_context('hosted_zone')))
        user_data.add_commands("""cat <<EOF > /tmp/recordset.json 
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "${record}",
        "Type": "A",
        "TTL": 600,
        "ResourceRecords": [
          {
            "Value": "${local_ip}"
          }
        ]
      }
    }
  ]
}
EOF""")
        user_data.add_commands(
            'aws route53 change-resource-record-sets --hosted-zone-id {} --change-batch file:///tmp/recordset.json'.format(
                workspaces_hosted_zone.hosted_zone_id))

        # Squidのインストールと設定を行う
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

# Allow access from localhost
http_access allow localhost

# Deny access from other than localnet
http_access deny !localnet

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

        # CloudWatchエージェントのインストールと設定を行う
        user_data.add_commands(
            'wget -nv https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm')
        user_data.add_commands('sudo rpm -U ./amazon-cloudwatch-agent.rpm')
        user_data.add_commands("""cat <<"EOF" > /opt/aws/amazon-cloudwatch-agent/bin/config.json
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root"
  },
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/var/log/squid/access.log",
            "log_group_name": "SquidAccessLogs",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/squid/cache.log",
            "log_group_name": "SquidCacheLogs",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  },
  "metrics": {
    "append_dimensions": {
      "AutoScalingGroupName": "${aws:AutoScalingGroupName}",
      "ImageId": "${aws:ImageId}",
      "InstanceId": "${aws:InstanceId}",
      "InstanceType": "${aws:InstanceType}"
    },
    "metrics_collected": {
      "disk": {
        "measurement": [
          "used_percent"
        ],
        "metrics_collection_interval": 60,
        "resources": [
          "*"
        ]
      },
      "mem": {
        "measurement": [
          "mem_used_percent"
        ],
        "metrics_collection_interval": 60
      }
    }
  }
}
EOF""")
        user_data.add_commands(
            '/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json -s')

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
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
        )

        # セキュリティーグループの設定
        proxy_asg.connections.allow_from_any_ipv4(
            ec2.Port.tcp(22)
        )
        # WorksSpacesインスタンスからのアクセスを許可
        proxy_asg.connections.allow_from(
            other=workspaces_workspaces_sg,
            port_range=ec2.Port.tcp(3128)
        )
        # VPCエンドポイントへのアクセスを許可
        proxy_asg.connections.allow_to(
            other=workspaces_endpoint_sg,
            port_range=ec2.Port.all_traffic()
        )

        # CloudWatchエージェント用のポリシーをアタッチ
        proxy_asg.role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchAgentServerPolicy'))

        # Route53にレコードを追加するためのポリシー
        route53_policy = iam.Policy(
            self, 'Route53Policy',
            statements=[
                iam.PolicyStatement(
                    actions=["route53:ChangeResourceRecordSets"],
                    resources=[workspaces_hosted_zone.hosted_zone_arn]
                )
            ]
        )
        proxy_asg.role.attach_inline_policy(route53_policy)

        self.output_props = props.copy()
        self.output_props['workspaces_proxy_sg'] = proxy_asg.connections.security_groups[0]

    @property
    def outputs(self):
        return self.output_props
