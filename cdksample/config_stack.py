from aws_cdk import (
    core,
    aws_config as config,
    aws_ec2 as ec2,
    aws_events_targets as targets,
    aws_iam as iam
)


class ConfigStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        alert_topic = props['alert_topic']
        workspaces_vpc = props['workspaces_vpc']
        log_bucket = props['log_bucket']

        default_vpc = ec2.Vpc.from_lookup(
            self, 'DefaultVpc',
            is_default=True
        )

        ################
        # Configの有効化の設定
        ################

        config_role = iam.Role(
            self, 'ConfigRole',
            assumed_by=iam.ServicePrincipal('config.amazonaws.com')
        )

        config_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSConfigRole'))

        recorder = config.CfnConfigurationRecorder(
            self, 'ConfigurationRecoder',
            role_arn=config_role.role_arn,
            recording_group={
                "allSupported": True,
                "includeGlobalResourceTypes": True
            }
        )

        channel = config.CfnDeliveryChannel(
            self, 'DeliveryChannel',
            s3_bucket_name=log_bucket.bucket_name,
            config_snapshot_delivery_properties=None
        )

        ################
        # ルールの作成
        ################

        cloudtrail_enabled_rule = config.ManagedRule(
            self, 'CloudTrailEnabled',
            identifier='CLOUD_TRAIL_ENABLED',
            config_rule_name='cloudtrail-enabled',
            description='AWS アカウントで AWS CloudTrail が有効になっているかどうかを確認します。オプションで、使用する S3 バケット、SNS トピック、および Amazon CloudWatch Logs ARN を指定できます。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.SIX_HOURS
        )
        cloudtrail_enabled_rule.node.add_dependency(recorder)
        cloudtrail_enabled_rule.on_compliance_change(
            'EventRule',
            target=targets.SnsTopic(alert_topic)
        )

        ec2_instance_no_public_ip_rule = config.ManagedRule(
            self, 'Ec2InstanceNoPublicIp',
            identifier='EC2_INSTANCE_NO_PUBLIC_IP',
            config_rule_name='ec2-instance-no-public-ip',
            description='Amazon Elastic Compute Cloud (Amazon EC2) インスタンスにパブリック IP が関連付けられているかどうかを確認します。Amazon EC2 インスタンス設定項目に publicIp フィールドが存在する場合、ルールは NON_COMPLIANT です。このルールは IPv4 にのみ適用されます。'
        )
        ec2_instance_no_public_ip_rule.scope_to_resource('AWS::EC2::Instance')
        ec2_instance_no_public_ip_rule.node.add_dependency(recorder)
        ec2_instance_no_public_ip_rule.on_compliance_change(
            'EventRule',
            target=targets.SnsTopic(alert_topic)
        )

        guardduty_enabled_centralized_rule = config.ManagedRule(
            self, 'GuarddutyEnabledCentralized',
            identifier='GUARDDUTY_ENABLED_CENTRALIZED',
            config_rule_name='guardduty-enabled-centralized',
            description='AWS アカウントおよびリージョンで、Amazon GuardDuty が有効になっているかどうかを確認します。一元管理用の AWS アカウントを指定した場合、ルールはそのアカウントでの GuardDuty の結果を評価します。GuardDuty が有効であれば、ルールは準拠しています。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.SIX_HOURS
        )
        guardduty_enabled_centralized_rule.node.add_dependency(recorder)
        guardduty_enabled_centralized_rule.on_compliance_change(
            'EventRule',
            target=targets.SnsTopic(alert_topic)
        )

        iam_password_policy_rule = config.ManagedRule(
            self, 'IamPasswordPolicyConfig',
            identifier='IAM_PASSWORD_POLICY',
            config_rule_name='iam-password-policy',
            description='IAM ユーザーのアカウントパスワードポリシーが、指定された要件を満たすかどうか確認します。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.SIX_HOURS,
            input_parameters={
                "RequireUppercaseCharacters": True,
                "RequireLowercaseCharacters": True,
                "RequireSymbols": True,
                "RequireNumbers": True,
                "MinimumPasswordLength": 8,
                "PasswordReusePrevention": 10,
                "MaxPasswordAge": 90
            }
        )
        iam_password_policy_rule.node.add_dependency(recorder)
        iam_password_policy_rule.on_compliance_change(
            'EventRule',
            target=targets.SnsTopic(alert_topic)
        )

        iam_root_access_key_check_rule = config.ManagedRule(
            self, 'IamRootAccessKeyCheck',
            identifier='IAM_ROOT_ACCESS_KEY_CHECK',
            config_rule_name='iam-root-access-key-check',
            description='root ユーザーアクセスキーが使用可能かどうかを確認します。ユーザーアクセスキーが存在しない場合、ルールは準拠しています。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.SIX_HOURS,
        )
        iam_root_access_key_check_rule.node.add_dependency(recorder)
        iam_root_access_key_check_rule.on_compliance_change(
            'EventRule',
            target=targets.SnsTopic(alert_topic)
        )

        iam_user_mfa_enabled_rule = config.ManagedRule(
            self, 'IamUserMfaEnabled',
            identifier='IAM_USER_MFA_ENABLED',
            config_rule_name='iam-user-mfa-enabled',
            description='AWS Identity and Access Management ユーザーの Multi-Factor Authentication (MFA) が有効かどうかを確認します。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.SIX_HOURS
        )
        iam_user_mfa_enabled_rule.node.add_dependency(recorder)
        iam_user_mfa_enabled_rule.on_compliance_change(
            'EventRule',
            target=targets.SnsTopic(alert_topic)
        )

        internet_gateway_authorized_vpc_only_rule = config.ManagedRule(
            self, 'InternetGatewayAuthorizedVpcOnly',
            identifier='INTERNET_GATEWAY_AUTHORIZED_VPC_ONLY',
            config_rule_name='internet-gateway-authorized-vpc-only',
            description='インターネットゲートウェイ (IGW) が承認された Amazon Virtual Private Cloud (VPC) にのみ接続されていることを確認します。IGW が承認された VPC に接続されていない場合、ルールは NON_COMPLIANT です。',
            input_parameters={
                "AuthorizedVpcIds": "{},{}".format(default_vpc.vpc_id, workspaces_vpc.vpc_id)
            }
        )
        internet_gateway_authorized_vpc_only_rule.scope_to_resource('AWS::EC2::InternetGateway')
        internet_gateway_authorized_vpc_only_rule.node.add_dependency(recorder)
        internet_gateway_authorized_vpc_only_rule.on_compliance_change(
            'EventRule',
            target=targets.SnsTopic(alert_topic)
        )

        multi_region_cloudtrail_enabled_rule = config.ManagedRule(
            self, 'MultiRegionCloudtrailEnabled',
            identifier='MULTI_REGION_CLOUD_TRAIL_ENABLED',
            config_rule_name='multi-region-cloudtrail-enabled',
            description='少なくとも 1 つのマルチリージョン AWS CloudTrail があることを確認します。証跡が入力パラメータと一致しない場合、ルールは準拠していません。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.SIX_HOURS
        )
        multi_region_cloudtrail_enabled_rule.node.add_dependency(recorder)
        multi_region_cloudtrail_enabled_rule.on_compliance_change(
            'EventRule',
            target=targets.SnsTopic(alert_topic)
        )

        redshift_cluster_public_access_check_rule = config.ManagedRule(
            self, 'RedshiftClusterPublicAccessCheck',
            identifier='REDSHIFT_CLUSTER_PUBLIC_ACCESS_CHECK',
            config_rule_name='redshift-cluster-public-access-check',
            description='Amazon Redshift クラスターがパブリックでアクセス可能になっていないかどうかを確認します。クラスター設定項目で publiclyAccessible フィールドが true の場合、ルールは NON_COMPLIANT です。'
        )
        redshift_cluster_public_access_check_rule.scope_to_resource('AWS::Redshift::Cluster')
        redshift_cluster_public_access_check_rule.node.add_dependency(recorder)
        redshift_cluster_public_access_check_rule.on_compliance_change(
            'EventRule',
            target=targets.SnsTopic(alert_topic)
        )

        root_account_mfa_enabled_rule = config.ManagedRule(
            self, 'RootAccountMfaEnabled',
            identifier='ROOT_ACCOUNT_MFA_ENABLED',
            config_rule_name='root-account-mfa-enabled',
            description='AWS アカウントの root ユーザーが、コンソールのサインインに Multi-Factor Authentication を必要とするかどうかを確認します。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.SIX_HOURS
        )
        root_account_mfa_enabled_rule.node.add_dependency(recorder)
        root_account_mfa_enabled_rule.on_compliance_change(
            'EventRule',
            target=targets.SnsTopic(alert_topic)
        )

        s3_bucket_public_read_prohibited_rule = config.ManagedRule(
            self, 'S3BucketPublicReadProhibited',
            identifier='S3_BUCKET_PUBLIC_READ_PROHIBITED',
            config_rule_name='s3-bucket-public-read-prohibited',
            description='S3 バケットが読み取りパブリックアクセスを許可していないことを確認します。S3 バケットポリシーまたはバケット ACL で読み取りパブリックアクセスを許可している場合、そのバケットは準拠していません。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.SIX_HOURS
        )
        s3_bucket_public_read_prohibited_rule.scope_to_resource('AWS::S3::Bucket')
        s3_bucket_public_read_prohibited_rule.node.add_dependency(recorder)
        s3_bucket_public_read_prohibited_rule.on_compliance_change(
            'EventRule',
            target=targets.SnsTopic(alert_topic)
        )

        s3_bucket_public_write_prohibited_rule = config.ManagedRule(
            self, 'S3BucketPublicWriteProhibited',
            identifier='S3_BUCKET_PUBLIC_WRITE_PROHIBITED',
            config_rule_name='s3-bucket-public-write-prohibited',
            description='S3 バケットが書き込みパブリックアクセスを許可していないことを確認します。S3 バケットポリシーまたはバケット ACL で書き込みパブリックアクセスを許可している場合、そのバケットは準拠していません。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.SIX_HOURS
        )
        s3_bucket_public_write_prohibited_rule.scope_to_resource('AWS::S3::Bucket')
        s3_bucket_public_write_prohibited_rule.node.add_dependency(recorder)
        s3_bucket_public_write_prohibited_rule.on_compliance_change(
            'EventRule',
            target=targets.SnsTopic(alert_topic)
        )

        sagemaker_notebook_no_direct_internet_access_rule = config.ManagedRule(
            self, 'SagemakerNotebookNoDirectInternetAccess',
            identifier='SAGEMAKER_NOTEBOOK_NO_DIRECT_INTERNET_ACCESS',
            config_rule_name='sagemaker-notebook-no-direct-internet-access',
            description='Amazon SageMaker ノートブックインスタンスに対して直接のインターネットアクセスが無効になっているかどうかを確認します。Amazon SageMaker ノートブックインスタンスがインターネット対応であれば、ルールは NON_COMPLIANT です。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.SIX_HOURS
        )
        sagemaker_notebook_no_direct_internet_access_rule.node.add_dependency(recorder)
        sagemaker_notebook_no_direct_internet_access_rule.on_compliance_change(
            'EventRule',
            target=targets.SnsTopic(alert_topic)
        )

        vpc_flow_logs_enabled_rule = config.ManagedRule(
            self, 'VpcFlowLogsEnabled',
            identifier='VPC_FLOW_LOGS_ENABLED',
            config_rule_name='vpc-flow-logs-enabled',
            description='Amazon Virtual Private Cloud フローログが見つかるかどうか、および Amazon VPC に対して有効になっているかどうかを確認します。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.SIX_HOURS
        )
        vpc_flow_logs_enabled_rule.node.add_dependency(recorder)
        vpc_flow_logs_enabled_rule.on_compliance_change(
            'EventRule',
            target=targets.SnsTopic(alert_topic)
        )

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
