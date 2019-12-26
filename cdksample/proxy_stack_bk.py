from aws_cdk import (
    core,
    aws_ec2 as ec2
)


class ProxyStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = props['workspaces_vpc']

        # EC2の作成
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/Instance.html

        # Proxy用セキュリティーグループ
        proxy_sg = ec2.SecurityGroup(
            self, 'ProxySg',
            vpc=vpc
        )
        proxy_sg.connections.allow_from_any_ipv4(
            ec2.Port.tcp(22)
        )

        # AWS::CloudFormation::Initを使いたいが、Instanceだとadd_overrideが実現できないのでCfnInstanceを使う
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/CfnInstance.html
        # https://cloudpack.media/48920
        # https://github.com/Noppy/EKSPoC_For_SecureEnvironment

        # Proxy用EC2ホスト
        # TODO
        # - AutoScalingGroupに変える
        proxy_host = ec2.CfnInstance(
            self, 'ProxyHost',
            image_id=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2).get_image(self).image_id,
            instance_type=ec2.InstanceType('t2.small').to_string(),
            key_name=self.node.try_get_context('key_name'),
            security_group_ids=[proxy_sg.security_group_id],
            subnet_id=vpc.select_subnets(subnet_type=ec2.SubnetType.PUBLIC).subnet_ids[0],
            tags=[core.CfnTag(key='Name', value='{}/{}'.format(self.stack_name, 'ProxyHost'))]
        )

        # ユーザーデータ
        user_data = ec2.UserData.for_linux()
        user_data.add_commands('yum update -y')
        user_data.add_commands(
            '/opt/aws/bin/cfn-init -v --stack {} --resource {} --region {} --configsets proxy_setup'.format(
                self.stack_name,
                proxy_host.logical_id,
                self.node.try_get_context('region')
            )
        )
        proxy_host.user_data = core.Fn.base64(user_data.render())

        # メタデータ
        proxy_host.add_override('Metadata', {
            'AWS::CloudFormation::Init': {
                'configSets': {
                    'proxy_setup': [
                        'install_squid',
                        'setup_squid'
                    ]
                },
                'install_squid': {
                    'packages': {
                        'yum': {
                            'squid': []
                        }
                    }
                },
                'setup_squid': {
                    'files': {
                        '/etc/squid/squid.conf': {
                            'content': """\
# Define local networks
acl localnet src 10.0.0.0/16

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
""",
                            'mode': '000640',
                            'owner': 'root',
                            'group': 'squid'
                        },
                        '/etc/squid/whitelist': {
                            'content': """\
# AWS Management Console
.aws.amazon.com
.amazonaws.com
.amazontrust.com
.cloudfront.net
.cloudfront.com
.sagemaker.aws
""",
                            'mode': '000640',
                            'owner': 'root',
                            'group': 'squid'
                        }
                    },
                    'services': {
                        'sysvinit': {
                            'squid': {
                                'enabled': True,
                                'ensureRunning': True,
                                'files': [
                                    '/etc/squid/squid.conf',
                                    '/etc/squid/whitelist.conf'
                                ]
                            }
                        }
                    }
                }
            }
        }
                                )

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
