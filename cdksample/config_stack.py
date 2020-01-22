from aws_cdk import (
    core,
    aws_config as config,
    aws_ec2 as ec2,
    aws_iam as iam
)


class ConfigStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        workspaces_vpc = props['workspaces_vpc']
        analytics_vpc = props['analytics_vpc']
        sap_vpc = props['sap_vpc']
        default_vpc = ec2.Vpc.from_lookup(
            self, 'DefaultVpc',
            is_default=True
        )
        log_bucket = props['log_bucket']

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
            # name='default',
            role_arn=config_role.role_arn,
            recording_group={
                "allSupported": True,
                "includeGlobalResourceTypes": True
            }
        )

        channel = config.CfnDeliveryChannel(
            self, 'DeliveryChannel',
            # name='default',
            s3_bucket_name=log_bucket.bucket_name,
            config_snapshot_delivery_properties=None
        )

        ################
        # ルールの作成
        ################

        cloudtrail_enabled_rule = config.ManagedRule(
            self, 'CloudTrailEabledRule',
            identifier='CLOUD_TRAIL_ENABLED',
            config_rule_name='cloudtrail-enabled',
            description='AWS アカウントで AWS CloudTrail が有効になっているかどうかを確認します。オプションで、使用する S3 バケット、SNS トピック、および Amazon CloudWatch Logs ARN を指定できます。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.ONE_HOUR
        )
        cloudtrail_enabled_rule.node.add_dependency(recorder)

        ec2_instance_no_public_ip_rule = config.ManagedRule(
            self, 'Ec2InstanceNoPublicIpRule',
            identifier='EC2_INSTANCE_NO_PUBLIC_IP',
            config_rule_name='ec2-instance-no-public-ip',
            description='Amazon Elastic Compute Cloud (Amazon EC2) インスタンスにパブリック IP が関連付けられているかどうかを確認します。Amazon EC2 インスタンス設定項目に publicIp フィールドが存在する場合、ルールは NON_COMPLIANT です。このルールは IPv4 にのみ適用されます。'
        )
        ec2_instance_no_public_ip_rule.scope_to_resource('AWS::EC2::Instance')
        ec2_instance_no_public_ip_rule.node.add_dependency(recorder)

        iam_password_policy_rule = config.ManagedRule(
            self, 'IamPasswordPolicyRule',
            identifier='IAM_PASSWORD_POLICY',
            config_rule_name='iam-password-policy',
            description='IAM ユーザーのアカウントパスワードポリシーが、指定された要件を満たすかどうか確認します。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.ONE_HOUR,
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

        iam_root_access_key_check_rule = config.ManagedRule(
            self, 'IamRootAccessKeyCheckRule',
            identifier='IAM_ROOT_ACCESS_KEY_CHECK',
            config_rule_name='iam-root-access-key-check',
            description='root ユーザーアクセスキーが使用可能かどうかを確認します。ユーザーアクセスキーが存在しない場合、ルールは準拠しています。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.ONE_HOUR,
        )
        iam_root_access_key_check_rule.node.add_dependency(recorder)

        iam_user_mfa_enabled_rule = config.ManagedRule(
            self, 'IamUserMfaEnabled',
            identifier='IAM_USER_MFA_ENABLED',
            config_rule_name='iam-user-mfa-enabled',
            description='AWS Identity and Access Management ユーザーの Multi-Factor Authentication (MFA) が有効かどうかを確認します。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.ONE_HOUR
        )
        iam_user_mfa_enabled_rule.node.add_dependency(recorder)

        internet_gateway_authorized_vpc_only_rule = config.ManagedRule(
            self, 'InternetGatewayAuthorizedVpcOnly',
            identifier='INTERNET_GATEWAY_AUTHORIZED_VPC_ONLY',
            config_rule_name='internet-gateway-authorized-vpc-only',
            description='インターネットゲートウェイ (IGW) が承認された Amazon Virtual Private Cloud (VPC) にのみ接続されていることを確認します。IGW が承認された VPC に接続されていない場合、ルールは NON_COMPLIANT です。',
            input_parameters={
                "AuthorizedVpcIds": "{},{},{}".format(default_vpc.vpc_id, workspaces_vpc.vpc_id, sap_vpc.vpc_id)
            }
        )
        internet_gateway_authorized_vpc_only_rule.scope_to_resource('AWS::EC2::InternetGateway')
        internet_gateway_authorized_vpc_only_rule.node.add_dependency(recorder)

        root_account_mfa_enabled_rule = config.ManagedRule(
            self, 'RootAccountMfaEnabled',
            identifier='ROOT_ACCOUNT_MFA_ENABLED',
            config_rule_name='root-account-mfa-enabled',
            description='AWS アカウントの root ユーザーが、コンソールのサインインに Multi-Factor Authentication を必要とするかどうかを確認します。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.ONE_HOUR
        )
        root_account_mfa_enabled_rule.node.add_dependency(recorder)

        s3_bucket_public_read_prohibited_rule = config.ManagedRule(
            self, 'S3BucketPublicReadProhibited',
            identifier='S3_BUCKET_PUBLIC_READ_PROHIBITED',
            config_rule_name='s3-bucket-public-read-prohibited',
            description='S3 バケットが読み取りパブリックアクセスを許可していないことを確認します。S3 バケットポリシーまたはバケット ACL で読み取りパブリックアクセスを許可している場合、そのバケットは準拠していません。',
            maximum_execution_frequency=config.MaximumExecutionFrequency.ONE_HOUR
        )
        s3_bucket_public_read_prohibited_rule.scope_to_resource('AWS::S3::Bucket')
        s3_bucket_public_read_prohibited_rule.node.add_dependency(recorder)

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
