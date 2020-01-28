from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_route53 as route53
)


class WorkSpacesVpcStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPCの作成
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/Vpc.html

        vpc = ec2.Vpc(
            self, 'VPC',
            cidr=self.node.try_get_context('workspaces_vpc_cidr'),
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name='Public',
                    subnet_type=ec2.SubnetType.PUBLIC
                ),
                ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name='Private',
                    subnet_type=ec2.SubnetType.PRIVATE
                ),
                ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name='Isolated',
                    subnet_type=ec2.SubnetType.ISOLATED
                )
            ]
        )

        # VPCエンドポイントのためのセキュリティーグループ
        endpoint_sg = ec2.SecurityGroup(
            self, 'EndpointSecurityGroup',
            vpc=vpc
        )

        # WorkSpacesのインスタンスのためのセキュリティーグループ
        workspaces_sg = ec2.SecurityGroup(
            self, 'WorkSpacesSecurityGroup',
            vpc=vpc
        )
        # VPCエンドポイントへのアクセスを許可
        workspaces_sg.connections.allow_to(
            other=endpoint_sg,
            port_range=ec2.Port.all_traffic()
        )

        # CloudWatchのVPCエンドポイントの作成
        # cloudwatch_endpoint = vpc.add_interface_endpoint(
        #     id='CloudWatchEndpoint',
        #     service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH,
        #     private_dns_enabled=True,
        #     security_groups=[endpoint_sg],
        #     subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        # )
        # CloudWatch LogsのVPCエンドポイントの作成
        cloudwatch_logs_endpoint = vpc.add_interface_endpoint(
            id='CloudWatchLogsEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            private_dns_enabled=True,
            security_groups=[endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )

        # プライベートホストゾーンの作成
        hosted_zone = route53.PrivateHostedZone(
            self, 'HostedZone',
            zone_name=self.node.try_get_context('proxy_server')['domain'],
            vpc=vpc
        )

        self.output_props = props.copy()
        self.output_props['workspaces_vpc'] = vpc
        self.output_props['workspaces_endpoint_sg'] = endpoint_sg
        self.output_props['workspaces_workspaces_sg'] = workspaces_sg
        self.output_props['workspaces_hosted_zone'] = hosted_zone

    @property
    def outputs(self):
        return self.output_props
