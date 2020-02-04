from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_route53 as route53
)


class NetworkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ################
        # VPCの作成
        ################

        # WorkSpaces用VPCの作成
        workspaces_vpc = ec2.Vpc(
            self, 'WorkSpacesVPC',
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

        # 分析用VPCの作成
        analytics_vpc = ec2.Vpc(
            self, 'AnalyticsVPC',
            cidr=self.node.try_get_context('analytics_vpc_cidr'),
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    cidr_mask=24,
                    name='Private',
                    subnet_type=ec2.SubnetType.ISOLATED
                )
            ]
        )

        ################
        # VPCピアリングの設定
        ################

        # WorkSpaces用VPCから分析用VPCへのピアリング
        workspaces_to_analytics_vpc_peering = ec2.CfnVPCPeeringConnection(
            self, 'WorkSpacesToAnalyticsVPCPeering',
            vpc_id=workspaces_vpc.vpc_id,
            peer_vpc_id=analytics_vpc.vpc_id,
            tags=[core.CfnTag(key='Name', value='{}/WorkSpacesToAnalyticsVPCPeering'.format(self.stack_name))]
        )

        # WorkSpaces用VPCのIsolated Subnetから分析用VPCとSAP用VPCへのルート
        for subnet in workspaces_vpc.select_subnets(subnet_type=ec2.SubnetType.ISOLATED).subnets:
            analytics_route = ec2.CfnRoute(
                self, 'AnalyticsPeerRoute{}'.format(subnet.to_string()),
                route_table_id=subnet.route_table.route_table_id,
                destination_cidr_block=analytics_vpc.vpc_cidr_block,
                vpc_peering_connection_id=workspaces_to_analytics_vpc_peering.ref
            )

        # 分析用VPCのIsolated SubnetからWorkSpaces用VPCへのルート
        for subnet in analytics_vpc.select_subnets(subnet_type=ec2.SubnetType.ISOLATED).subnets:
            route = ec2.CfnRoute(
                self, 'PeerRoute{}'.format(subnet.to_string()),
                route_table_id=subnet.route_table.route_table_id,
                destination_cidr_block=workspaces_vpc.vpc_cidr_block,
                vpc_peering_connection_id=workspaces_to_analytics_vpc_peering.ref
            )

        ################
        # セキュリティグループの作成
        ################

        # WorkSpaces用VPCのVPCエンドポイントのためのセキュリティーグループ
        workspaces_vpc_endpoint_sg = ec2.SecurityGroup(
            self, 'WorkSpacesVPCEndpointSecurityGroup',
            vpc=workspaces_vpc
        )
        # 分析用VPCのVPCエンドポイントのセキュリティーグループ
        analytics_vpc_endpoint_sg = ec2.SecurityGroup(
            self, 'AnalyticsVPCEndpointSecurityGroup',
            vpc=analytics_vpc
        )
        # Bastion用セキュリティーグループ
        bastion_sg = ec2.SecurityGroup(
            self, 'BastionSecurityGroup',
            vpc=workspaces_vpc
        )
        # Proxyインスタンスのセキュリティーグループ
        proxy_sg = ec2.SecurityGroup(
            self, 'ProxySecurityGroup',
            vpc=workspaces_vpc
        )
        # WorkSpacesインスタンスのセキュリティーグループ
        workspaces_sg = ec2.SecurityGroup(
            self, 'WorkSpacesSecurityGroup',
            vpc=workspaces_vpc
        )
        # RedShiftクラスターのセキュリティグループ
        redshift_sg = ec2.SecurityGroup(
            self, 'RedshiftSecurityGroup',
            vpc=analytics_vpc
        )
        # Notebookインスタンスのセキュリティーグループ
        notebook_sg = ec2.SecurityGroup(
            self, 'NotebookSecurityGroup',
            vpc=analytics_vpc
        )

        ################
        # セキュリティグループ間の通信の設定
        ################

        # WorkSpacesのVPCエンドポイントへのアクセス許可
        workspaces_vpc_endpoint_sg.add_ingress_rule(
            workspaces_sg,
            ec2.Port.all_traffic()
        )
        workspaces_vpc_endpoint_sg.add_ingress_rule(
            proxy_sg,
            ec2.Port.all_traffic()
        )

        # AnalyticsのVPCエンドポイントへのアクセス許可
        analytics_vpc_endpoint_sg.add_ingress_rule(
            redshift_sg,
            ec2.Port.all_traffic()
        )
        analytics_vpc_endpoint_sg.add_ingress_rule(
            notebook_sg,
            ec2.Port.all_traffic()
        )

        # BastionへのSSHを許可
        bastion_sg.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(22)
        )
        # ProxyへのSSHを許可
        proxy_sg.add_ingress_rule(
            bastion_sg,
            ec2.Port.tcp(22)
        )
        proxy_sg.add_ingress_rule(
            workspaces_sg,
            ec2.Port.tcp(22)
        )
        # WorksSpacesからProxyのSquidへのアクセスを許可
        proxy_sg.add_ingress_rule(
            workspaces_sg,
            ec2.Port.tcp(3128)
        )
        # WorksSpacesからRedshiftへのアクセスを許可
        redshift_sg.add_ingress_rule(
            workspaces_sg,
            ec2.Port.tcp(self.node.try_get_context('redshift')['port'])
        )
        # NotebookからRedShiftへのアクセスを許可
        redshift_sg.add_ingress_rule(
            notebook_sg,
            ec2.Port.tcp(self.node.try_get_context('redshift')['port'])
        )

        ################
        # VPCエンドポイントの作成
        ################

        # WorkSpaces用にVPCのCloudWatchのVPCエンドポイントを作成
        # このエンドポイントが存在するとSimple ADの作成に失敗するのでコメントアウト
        # workspaces_vpc_cloudwatch_endpoint = workspaces_vpc.add_interface_endpoint(
        #     id='WorkSpacesVPCCloudWatchEndpoint',
        #     service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH,
        #     private_dns_enabled=True,
        #     security_groups=[workspaces_vpc_endpoint_sg],
        #     subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        # )
        # 分析用VPCにCloudWatchのVPCエンドポイントを作成
        analytics_vpc_cloudwatch_endpoint = analytics_vpc.add_interface_endpoint(
            id='AnalyticsVPCCloudWatchEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH,
            private_dns_enabled=True,
            security_groups=[analytics_vpc_endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        # WorkSpaces用VPCにCloudWatch LogsのVPCエンドポイントを作成
        workspaces_vpc_cloudwatch_logs_endpoint = workspaces_vpc.add_interface_endpoint(
            id='WorkSpacesVPCCloudWatchLogsEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            private_dns_enabled=True,
            security_groups=[workspaces_vpc_endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        # 分析用VPCにCloudWatch LogsのVPCエンドポイントを作成
        analytics_vpc_cloudwatch_logs_endpoint = analytics_vpc.add_interface_endpoint(
            id='AnalyticsVPCCloudWatchLogsEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS,
            private_dns_enabled=True,
            security_groups=[analytics_vpc_endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        # WorkSpaces用VPCにSageMaker Notebookのエンドポイント作成
        workspaces_vpc_sagemaker_notebook_endpoint = workspaces_vpc.add_interface_endpoint(
            id='WorkSpacesVPCSageMakerNotebookEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.SAGEMAKER_NOTEBOOK,
            private_dns_enabled=True,
            security_groups=[workspaces_vpc_endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        # 分析用VPCにSageMaker APIのVPCエンドポイントを作成
        analytics_vpc_sagemaker_api_endpoint = analytics_vpc.add_interface_endpoint(
            id='AnalyticsVPCSageMakerApiEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.SAGEMAKER_API,
            private_dns_enabled=True,
            security_groups=[analytics_vpc_endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        # 分析用VPCにSageMaker RuntimeのVPCエンドポイントを作成
        analytics_vpc_sagemaker_runtime_endpoint = analytics_vpc.add_interface_endpoint(
            id='AnalyticsVPCSageMakerRuntimeEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.SAGEMAKER_RUNTIME,
            private_dns_enabled=True,
            security_groups=[analytics_vpc_endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        # 分析用VPCにSTSのVPCエンドポイントを作成
        analytics_vpc_sts_endpoint = analytics_vpc.add_interface_endpoint(
            id='AnalyticsVPCStsEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.STS,
            private_dns_enabled=True,
            security_groups=[analytics_vpc_endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        # 分析用VPCにECRのVPCエンドポイントを作成
        analytics_vpc_ecr_endpoint = analytics_vpc.add_interface_endpoint(
            id='AnalyticsVPCEcrEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.ECR,
            private_dns_enabled=True,
            security_groups=[analytics_vpc_endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        # 分析用VPCにECR DockerのVPCエンドポイントを作成
        analytics_vpc_ecr_docker_endpoint = analytics_vpc.add_interface_endpoint(
            id='AnalyticsVPCEcrDockerEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER,
            private_dns_enabled=True,
            security_groups=[analytics_vpc_endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
        # 分析用VPCにS3のVPCエンドポイントを作成
        analytics_vpc_s3_endpoint = analytics_vpc.add_gateway_endpoint(
            id='AnalyticsVPCS3Endpoint',
            service=ec2.GatewayVpcEndpointAwsService.S3,
            subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)]
        )

        ################
        # VPCエンドポイントポリシーの作成
        ################

        # 分析用VPCのS3のVPCエンドポイント
        analytics_vpc_s3_endpoint.add_to_policy(
            iam.PolicyStatement(
                principals=[iam.AnyPrincipal()],
                actions=[
                    "s3:GetObject*",
                    "s3:GetBucket*",
                    "s3:List*",
                    "s3:PutObject"
                ],
                resources=[
                    'arn:aws:s3:::data-{}-{}'.format(
                        self.node.try_get_context('account'),
                        self.node.try_get_context('bucket_suffix')
                    ),
                    'arn:aws:s3:::data-{}-{}/*'.format(
                        self.node.try_get_context('account'),
                        self.node.try_get_context('bucket_suffix')
                    ),
                    'arn:aws:s3:::log-{}-{}'.format(
                        self.node.try_get_context('account'),
                        self.node.try_get_context('bucket_suffix')
                    ),
                    'arn:aws:s3:::log-{}-{}/*'.format(
                        self.node.try_get_context('account'),
                        self.node.try_get_context('bucket_suffix')
                    )
                ]
            )
        )
        analytics_vpc_s3_endpoint.add_to_policy(
            iam.PolicyStatement(
                principals=[iam.AnyPrincipal()],
                actions=[
                    "s3:ListBucket",
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                resources=[
                    'arn:aws:s3:::sagemaker-{}-{}'.format(
                        self.node.try_get_context('account'),
                        self.node.try_get_context('bucket_suffix')
                    ),
                    'arn:aws:s3:::sagemaker-{}-{}/*'.format(
                        self.node.try_get_context('account'),
                        self.node.try_get_context('bucket_suffix')
                    )
                ]
            )
        )

        self.output_props = props.copy()
        self.output_props['workspaces_vpc'] = workspaces_vpc
        self.output_props['analytics_vpc'] = analytics_vpc
        self.output_props['workspaces_vpc_endpoint_sg'] = workspaces_vpc_endpoint_sg
        self.output_props['analytics_vpc_endpoint_sg'] = analytics_vpc_endpoint_sg
        self.output_props['bastion_sg'] = bastion_sg
        self.output_props['proxy_sg'] = proxy_sg
        self.output_props['workspaces_sg'] = workspaces_sg
        self.output_props['redshift_sg'] = redshift_sg
        self.output_props['notebook_sg'] = notebook_sg

    @property
    def outputs(self):
        return self.output_props
