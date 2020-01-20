from aws_cdk import (
    core,
    aws_ec2 as ec2
)


class AnalyticsVpcStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # VPCの作成
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/Vpc.html

        vpc = ec2.Vpc(
            self, 'VPC',
            cidr='10.2.0.0/16',
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name='Private',
                    subnet_type=ec2.SubnetType.ISOLATED
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
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        # CloudWatch LogsのVPCエンドポイントの作成
        cloudwatch_logs_endpoint = vpc.add_interface_endpoint(
            id='CloudWatchLogsEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            private_dns_enabled=True,
            security_groups=[endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        # SageMakerのVPCエンドポイントの作成
        sagemaker_notebook_endpoint = vpc.add_interface_endpoint(
            id='SageMakerNotebookEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.SAGEMAKER_NOTEBOOK,
            private_dns_enabled=True,
            security_groups=[endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        sagemaker_api_endpoint = vpc.add_interface_endpoint(
            id='SageMakerApiEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.SAGEMAKER_API,
            private_dns_enabled=True,
            security_groups=[endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        sagemaker_runtime_endpoint = vpc.add_interface_endpoint(
            id='SageMakerRuntimeEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.SAGEMAKER_RUNTIME,
            private_dns_enabled=True,
            security_groups=[endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        # STSのVPCエンドポイントの作成
        sts_endpoint = vpc.add_interface_endpoint(
            id='StsEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.STS,
            private_dns_enabled=True,
            security_groups=[endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        # ECRのVPCエンドポイントの作成
        ecr_endpoint = vpc.add_interface_endpoint(
            id='EcrEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.ECR,
            private_dns_enabled=True,
            security_groups=[endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        ecr_docker_endpoint = vpc.add_interface_endpoint(
            id='EcrDockerEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            private_dns_enabled=True,
            security_groups=[endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        # S3のVPCエンドポイントの作成
        s3_endpoint = vpc.add_gateway_endpoint(
            id='S3Endpoint',
            service=ec2.GatewayVpcEndpointAwsService.S3,
            subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)]
        )

        self.output_props = props.copy()
        self.output_props['analytics_vpc'] = vpc
        self.output_props['analytics_endpoint_sg'] = endpoint_sg

    @property
    def outputs(self):
        return self.output_props
