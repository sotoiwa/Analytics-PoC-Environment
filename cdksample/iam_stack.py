from aws_cdk import (
    core,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager
)


class IamStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # IAM
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_iam.html

        ################
        # IAMグループの作成
        ################

        # 全体管理者グループ
        admin_group = iam.Group(
            self, 'AdminGroup',
            group_name='AdminGroup'
        )
        # 環境管理者グループ
        # コスト管理、S3管理、システム管理のロールを兼ねるグループ
        environment_admin_group = iam.Group(
            self, 'EnvironmentAdminGroup',
            group_name='EnvironmentAdminGroup'
        )
        # セキュリティ監査者グループ
        # セキュリティ監査とKMS管理のロールを兼ねるグループ
        security_audit_group = iam.Group(
            self, 'SecurityAuditGroup',
            group_name='SecurityAuditGroup'
        )
        # 分析者グループ
        data_scientist_group = iam.Group(
            self, 'DataScientistGroup',
            group_name='DataScientistGroup'
        )

        ################
        # IAMユーザーの作成
        ################

        # 作成したユーザーのパスワードはSecretManagerに格納する

        # 後でまとめてリソースポリシーを設定するためリスト化しておく

        # customer_keyの使用を許可するユーザーのリスト
        customer_key_encrypt_decrypt_users = []
        # data_bucketの更新を許可するユーザーのリスト
        data_bucket_read_write_users = []
        # log_bucketの参照を許可するユーザーのリスト
        log_bucket_read_users = []

        # 全体管理者ユーザーの作成
        admin_user_names = self.node.try_get_context('admin_user_names')
        for user_name in admin_user_names:
            secret = secretsmanager.Secret(self, '{}-Secrets'.format(user_name))
            user = iam.User(
                self, user_name,
                user_name=user_name,
                password=secret.secret_value,
                password_reset_required=True
            )
            user.add_to_group(admin_group)
            # customer_keyの使用を許可するリストに追加
            customer_key_encrypt_decrypt_users.append(user)
            # data_bucketの更新を許可するリストに追加
            data_bucket_read_write_users.append(user)

        # 環境管理者ユーザーの作成
        environment_admin_user_names = self.node.try_get_context('environment_admin_user_names')
        for user_name in environment_admin_user_names:
            secret = secretsmanager.Secret(self, '{}-Secrets'.format(user_name))
            user = iam.User(
                self, user_name,
                user_name=user_name,
                password=secret.secret_value,
                password_reset_required=True
            )
            # ユーザーをグループに追加
            user.add_to_group(environment_admin_group)
            # customer_keyの使用を許可するリストに追加
            customer_key_encrypt_decrypt_users.append(user)

        # セキュリティー監査ユーザーの作成
        security_audit_user_names = self.node.try_get_context('security_audit_user_names')
        for user_name in security_audit_user_names:
            secret = secretsmanager.Secret(self, '{}-Secrets'.format(user_name))
            user = iam.User(
                self, user_name,
                user_name=user_name,
                password=secret.secret_value,
                password_reset_required=True
            )
            # ユーザーをグループに追加
            user.add_to_group(security_audit_group)
            # log_bucketの参照を許可するリストに追加
            log_bucket_read_users.append(user)

        # 分析者ユーザーの作成
        data_scientist_user_names = self.node.try_get_context('data_scientist_user_names')
        for user_name in data_scientist_user_names:
            secret = secretsmanager.Secret(self, '{}-Secrets'.format(user_name))
            user = iam.User(
                self, user_name,
                user_name=user_name,
                password=secret.secret_value,
                password_reset_required=True
            )
            # ユーザーをグループに追加
            user.add_to_group(data_scientist_group)
            # customer_keyの使用を許可するリストに追加
            customer_key_encrypt_decrypt_users.append(user)
            # data_bucketの更新を許可するリストに追加
            data_bucket_read_write_users.append(user)

        ################
        # 管理者グループ個別のIAMポリシー設定
        ################

        # 管理者グループ
        admin_group.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AdministratorAccess'))

        ################
        # 環境管理者グループ個別のIAMポリシー設定
        ################

        # コスト管理用のAWS管理ポリシー
        environment_admin_group.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('job-function/Billing'))
        # S3管理用のカスタマー管理ポリシー
        # TODO アクションを絞る
        s3_admin_policy = iam.ManagedPolicy(
            self, 'S3AdminPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=["s3:*"],
                    resources=["*"]
                )
            ]
        )
        environment_admin_group.add_managed_policy(s3_admin_policy)
        # システム管理用のカスタマー管理ポリシー
        system_admin_policy = iam.ManagedPolicy(
            self, 'SystemAdminPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "ec2:*",
                        "workspaces:*",
                        "redshift:*",
                        "elasticmapreduce:*",
                        "sagemaker:*",
                        "quicksight:*"
                    ],
                    resources=["*"]
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.DENY,
                    actions=[
                        "ec2:*Vpc*",
                        "ec2:AttachVpnGateway",
                        "ec2:DetachVpnGateway",
                        "ec2:CreateInternetGateway",
                        "ec2:ModifySnapshotAttribute",
                        "ec2:ModifyImageAttribute"
                    ],
                    resources=["*"]
                ),
                iam.PolicyStatement(
                    actions=[
                        "cloudtrail:LookupEvents",
                        "cloudtrail:GetTrail",
                        "cloudtrail:ListTrails",
                        "cloudtrail:ListPublicKeys",
                        "cloudtrail:ListTags",
                        "cloudtrail:GetTrailStatus",
                        "cloudtrail:GetEventSelectors",
                        "cloudtrail:GetInsightSelectors",
                        "cloudtrail:DescribeTrails"
                    ],
                    resources=["*"]
                ),
                iam.PolicyStatement(
                    actions=[
                        "cloudwatch:DescribeInsightRules",
                        "cloudwatch:GetDashboard",
                        "cloudwatch:GetInsightRuleReport",
                        "cloudwatch:GetMetricData",
                        "cloudwatch:GetMetricStatistics",
                        "cloudwatch:ListMetrics",
                        "cloudwatch:DescribeAnomalyDetectors",
                        "cloudwatch:DescribeAlarmHistory",
                        "cloudwatch:DescribeAlarmsForMetric",
                        "cloudwatch:ListDashboards",
                        "cloudwatch:ListTagsForResource",
                        "cloudwatch:DescribeAlarms",
                        "cloudwatch:GetMetricWidgetImage"
                    ],
                    resources=["*"]
                ),
                iam.PolicyStatement(
                    actions=[
                        "logs:ListTagsLogGroup",
                        "logs:DescribeQueries",
                        "logs:GetLogRecord",
                        "logs:DescribeLogGroups",
                        "logs:DescribeLogStreams",
                        "logs:DescribeSubscriptionFilters",
                        "logs:StartQuery",
                        "logs:DescribeMetricFilters",
                        "logs:StopQuery",
                        "logs:TestMetricFilter",
                        "logs:GetLogDelivery",
                        "logs:ListLogDeliveries",
                        "logs:DescribeExportTasks",
                        "logs:GetQueryResults",
                        "logs:GetLogEvents",
                        "logs:FilterLogEvents",
                        "logs:GetLogGroupFields",
                        "logs:DescribeResourcePolicies",
                        "logs:DescribeDestinations"
                    ],
                    resources=["*"]
                ),
                iam.PolicyStatement(
                    actions=[
                        "events:DescribeRule",
                        "events:DescribePartnerEventSource",
                        "events:DescribeEventSource",
                        "events:ListEventBuses",
                        "events:TestEventPattern",
                        "events:DescribeEventBus",
                        "events:ListPartnerEventSourceAccounts",
                        "events:ListRuleNamesByTarget",
                        "events:ListPartnerEventSources",
                        "events:ListEventSources",
                        "events:ListTagsForResource",
                        "events:ListRules",
                        "events:ListTargetsByRule"
                    ],
                    resources=["*"]
                ),
            ]
        )
        environment_admin_group.add_managed_policy(system_admin_policy)

        ################
        # セキュリティ監査者グループ個別のIAMポリシー設定
        ################

        # セキュリティ監査者用のカスタマー管理ポリシー
        security_audit_policy = iam.ManagedPolicy(
            self, 'SecurityAudit',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "cloudtrail:*",
                        "cloudwatch:*",
                        "logs:*",
                        "events:*",
                        "config:*",
                        "guardduty:*"
                    ],
                    resources=["*"]
                )
            ]
        )
        security_audit_group.add_managed_policy(security_audit_policy)
        # KMS管理用のカスタマー管理ポリシー
        kms_admin_policy = iam.ManagedPolicy(
            self, 'KmsAdminPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=["kms:*"],
                    resources=["*"]
                )
            ]
        )
        security_audit_group.add_managed_policy(kms_admin_policy)

        ################
        # 分析者グループ個別のIAMポリシー設定
        ################

        # 分析者用のカスタマー管理ポリシー
        data_scientist_policy = iam.ManagedPolicy(
            self, 'DataScientistPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "redshift:*",
                        "elasticmapreduce:*",
                        "sagemaker:*",
                        "quicksight:*"
                    ],
                    resources=["*"]
                )
            ]
        )
        data_scientist_group.add_managed_policy(data_scientist_policy)

        ################
        # 自身のパスワードとMFAの設定を許可するIAMポリシー
        ################

        # https://dev.classmethod.jp/cloud/aws/iam-difference-between-changepassword-and-updateloginprofile/

        # パスワードとMFA設定用ポリシー
        password_mfa_policy = iam.ManagedPolicy(
            self, 'PasswordMfaPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "iam:ChangePassword",
                        # "iam:CreateAccessKey",
                        "iam:CreateVirtualMFADevice",
                        "iam:DeactivateMFADevice",
                        # "iam:DeleteAccessKey",
                        "iam:DeleteVirtualMFADevice",
                        "iam:EnableMFADevice",
                        "iam:GetAccountPasswordPolicy",
                        # "iam:UpdateAccessKey",
                        # "iam:UpdateSigningCertificate",
                        # "iam:UploadSigningCertificate",
                        "iam:UpdateLoginProfile",
                        "iam:ResyncMFADevice"
                    ],
                    resources=[
                        'arn:aws:iam::{}:user/${{aws:username}}'.format(self.node.try_get_context('account')),
                        'arn:aws:iam::{}:mfa/${{aws:username}}'.format(self.node.try_get_context('account'))
                    ]
                ),
                iam.PolicyStatement(
                    actions=[
                        "iam:Get*",
                        "iam:List*"
                    ],
                    resources=["*"]
                )
            ]
        )

        # カスタマー管理ポリシーをグループにアタッチ
        for group in [admin_group, environment_admin_group, security_audit_group, data_scientist_group]:
            group.add_managed_policy(password_mfa_policy)

        ################
        # IPアドレス制限を行うIAMポリシー
        ################

        # IPアドレス制限を行うカスタマー管理ポリシー
        ip_address_policy = iam.ManagedPolicy(
            self, 'IpAddressPolicy',
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.DENY,
                    not_actions=['iam:ChangePassword'],
                    resources=['*'],
                    conditions={
                        'NotIpAddress': {
                            'aws:SourceIp': self.node.try_get_context('nat_gateway_eips')
                        }
                    }
                )
            ]
        )
        # カスタマー管理ポリシーをグループにアタッチ
        for group in [admin_group, environment_admin_group, security_audit_group, data_scientist_group]:
            group.add_managed_policy(ip_address_policy)

        self.output_props = props.copy()
        self.output_props['admin_group'] = admin_group
        self.output_props['environment_admin_group'] = environment_admin_group
        self.output_props['security_audit_group'] = security_audit_group
        self.output_props['data_scientist_group'] = data_scientist_group
        self.output_props['log_bucket_read_users'] = log_bucket_read_users
        self.output_props['customer_key_encrypt_decrypt_users'] = customer_key_encrypt_decrypt_users
        self.output_props['data_bucket_read_write_users'] = data_bucket_read_write_users

    @property
    def outputs(self):
        return self.output_props
