from aws_cdk import (
    core,
    aws_iam as iam
)


class IamStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ################
        # IAMロールの作成
        ################

        # 全体管理ロール
        admin_role = iam.Role(
            self, 'AdminRole',
            role_name='AdminRole',
            assumed_by=iam.AccountRootPrincipal(),
        )
        admin_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AdministratorAccess'))

        # コスト管理ロール
        cost_admin_role = iam.Role(
            self, 'CostAdminRole',
            role_name='CostAdminRole',
            assumed_by=iam.AccountRootPrincipal(),
        )
        admin_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('job-function/Billing'))

        # S3管理ロール
        s3_admin_role = iam.Role(
            self, 'S3AdminRole',
            role_name='S3AdminRole',
            assumed_by=iam.AccountRootPrincipal()
        )
        s3_admin_role_policy = iam.ManagedPolicy(
            self, 'S3AdminRolePolicy',
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "s3:*"
                    ],
                    resources=["*"]
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.DENY,
                    actions=[
                        "s3:PutBucketPublicAccessBlock",
                        "s3:PutAccessPointPolicy"
                    ],
                    resources=[
                        "arn:aws:s3:::*",
                        "arn:aws:s3:*:*:accesspoint/*"
                    ]
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.DENY,
                    actions=[
                        "s3:PutAccountPublicAccessBlock"
                    ],
                    resources=["*"]
                )
            ]
        )
        s3_admin_role.add_managed_policy(s3_admin_role_policy)

        # システム管理ロール
        system_admin_role = iam.Role(
            self, 'SystemAdminRole',
            role_name='SystemAdminRole',
            assumed_by=iam.AccountRootPrincipal()
        )
        system_admin_role_policy = iam.ManagedPolicy(
            self, 'SystemAdminRolePolicy',
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
        system_admin_role.add_managed_policy(system_admin_role_policy)

        # セキュリティ監査ロール
        security_audit_role = iam.Role(
            self, 'SecurityAuditRole',
            role_name='SecurityAuditRole',
            assumed_by=iam.AccountRootPrincipal()
        )
        security_audit_role_policy = iam.ManagedPolicy(
            self, 'SecurityAuditRolePolicy',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "cloudtrail:*",
                        "cloudwatch:*",
                        "logs:*",
                        "events:*",
                        "config:*",
                        "guardduty:*",
                        "s3:ListAllMyBuckets"
                    ],
                    resources=["*"]
                ),
                iam.PolicyStatement(
                    actions=[
                        "s3:ListBucket"
                    ],
                    resources=["arn:aws:s3:::*"]
                ),
                iam.PolicyStatement(
                    actions=[
                        "s3:GetObject"
                    ],
                    resources=[
                        'arn:aws:s3:::log-{}-{}'.format(
                            self.node.try_get_context('account'),
                            self.node.try_get_context('bucket_suffix')
                        ),
                        'arn:aws:s3:::log-{}-{}/*'.format(
                            self.node.try_get_context('account'),
                            self.node.try_get_context('bucket_suffix')
                        ),
                    ]
                ),
            ]
        )
        security_audit_role.add_managed_policy(security_audit_role_policy)

        # KMS管理ロール作成
        kms_admin_role = iam.Role(
            self, 'KmsAdminRole',
            role_name='KmsAdminRole',
            assumed_by=iam.AccountRootPrincipal()
        )
        kms_admin_role_policy = iam.ManagedPolicy(
            self, 'KmsAdminRolePolicy',
            statements=[
                iam.PolicyStatement(
                    actions=["kms:*"],
                    resources=["*"]
                )
            ]
        )
        kms_admin_role.add_managed_policy(kms_admin_role_policy)

        # 分析ロール作成
        data_scientist_role = iam.Role(
            self, 'DataScientistRole',
            role_name='DataScientistRole',
            assumed_by=iam.AccountRootPrincipal()
        )
        data_scientist_role_policy = iam.ManagedPolicy(
            self, 'DataScientistRolePolicy',
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
        data_scientist_role.add_managed_policy(data_scientist_role_policy)

        ################
        # IAMグループの作成
        ################

        # 全体管理者グループ
        # 全体管理ロールにスイッチ可能
        admin_group = iam.Group(
            self, 'AdminGroup',
            group_name='AdminGroup'
        )
        admin_group_policy = iam.ManagedPolicy(
            self, 'AdminGroupPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "sts:AssumeRole"
                    ],
                    resources=[
                        admin_role.role_arn
                    ]
                )
            ]
        )
        admin_group.add_managed_policy(admin_group_policy)

        # 環境管理者グループ
        # コスト管理ロール、S3管理ロール、システム管理ロールにスイッチ可能
        environment_admin_group = iam.Group(
            self, 'EnvironmentAdminGroup',
            group_name='EnvironmentAdminGroup'
        )
        environment_admin_group_policy = iam.ManagedPolicy(
            self, 'EnvironmentAdminGroupPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    resources=[
                        system_admin_role.role_arn,
                        cost_admin_role.role_arn,
                        s3_admin_role.role_arn
                    ]
                )
            ]
        )
        environment_admin_group.add_managed_policy(environment_admin_group_policy)

        # セキュリティ監査者グループ
        # セキュリティ監査ロール、KMS管理ロールにスイッチ可能
        security_audit_group = iam.Group(
            self, 'SecurityAuditGroup',
            group_name='SecurityAuditGroup'
        )
        security_audit_group_policy = iam.ManagedPolicy(
            self, 'SecurityAuditGroupPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    resources=[
                        security_audit_role.role_arn,
                        kms_admin_role.role_arn
                    ]
                )
            ]
        )
        security_audit_group.add_managed_policy(security_audit_group_policy)

        # 分析者グループ
        # 分析者ロールにスイッチ可能
        data_scientist_group = iam.Group(
            self, 'DataScientistGroup',
            group_name='DataScientistGroup'
        )
        data_scientist_group_policy = iam.ManagedPolicy(
            self, 'DataScientistGroupPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    resources=[
                        data_scientist_role.role_arn
                    ]
                )
            ]
        )
        data_scientist_group.add_managed_policy(data_scientist_group_policy)

        ################
        # IAMユーザーの作成
        ################

        default_user_password = self.node.try_get_context('default_user_password')

        # 全体管理者ユーザーの作成
        admin_user_names = self.node.try_get_context('admin_user_names')
        for user_name in admin_user_names:
            user = iam.User(
                self, user_name,
                user_name=user_name,
                password=core.SecretValue.plain_text(default_user_password),
                password_reset_required=True
            )
            user.add_to_group(admin_group)

        # 環境管理者ユーザーの作成
        environment_admin_user_names = self.node.try_get_context('environment_admin_user_names')
        for user_name in environment_admin_user_names:
            user = iam.User(
                self, user_name,
                user_name=user_name,
                password=core.SecretValue.plain_text(default_user_password),
                password_reset_required=True
            )
            user.add_to_group(environment_admin_group)

        # セキュリティー監査ユーザーの作成
        security_audit_user_names = self.node.try_get_context('security_audit_user_names')
        for user_name in security_audit_user_names:
            user = iam.User(
                self, user_name,
                user_name=user_name,
                password=core.SecretValue.plain_text(default_user_password),
                password_reset_required=True
            )
            user.add_to_group(security_audit_group)

        # 分析者ユーザーの作成
        data_scientist_user_names = self.node.try_get_context('data_scientist_user_names')
        for user_name in data_scientist_user_names:
            user = iam.User(
                self, user_name,
                user_name=user_name,
                password=core.SecretValue.plain_text(default_user_password),
                password_reset_required=True
            )
            user.add_to_group(data_scientist_group)

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
        self.output_props['admin_role'] = admin_role
        self.output_props['cost_admin_role'] = cost_admin_role
        self.output_props['s3_admin_role'] = s3_admin_role
        self.output_props['system_admin_role'] = system_admin_role
        self.output_props['security_audit_role'] = security_audit_role
        self.output_props['kms_admin_role'] = kms_admin_role
        self.output_props['data_scientist_role'] = data_scientist_role

    @property
    def outputs(self):
        return self.output_props
