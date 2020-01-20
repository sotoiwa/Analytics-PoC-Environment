from aws_cdk import (
    core,
    aws_ec2 as ec2
)


class SapVpcStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPCの作成
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/Vpc.html

        vpc = ec2.Vpc(
            self, 'VPC',
            cidr='10.3.0.0/16',
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
                )
            ]
        )

        # VPCエンドポイントのためのセキュリティーグループ
        endpoint_sg = ec2.SecurityGroup(
            self, 'EndpointSecurityGroup',
            vpc=vpc
        )

        # CloudWatchのVPCエンドポイントの作成
        cloudwatch_endpoint = vpc.add_interface_endpoint(
            id='CloudWatchEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH,
            private_dns_enabled=True,
            security_groups=[endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE)
        )
        # CloudWatch LogsのVPCエンドポイントの作成
        cloudwatch_logs_endpoint = vpc.add_interface_endpoint(
            id='CloudWatchLogsEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            private_dns_enabled=True,
            security_groups=[endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE)
        )

        self.output_props = props.copy()
        self.output_props['sap_vpc'] = vpc
        self.output_props['sap_endpoint_sg'] = endpoint_sg

    @property
    def outputs(self):
        return self.output_props
