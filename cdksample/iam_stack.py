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
        cost_admin_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('job-function/Billing'))

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
                        "ec2:Describe*",
                        "elasticloadbalancing:Describe*",
                        "autoscaling:Describe*",
                        "workspaces:Describe*",
                        "workspaces:List*",
                        "sns:Get*",
                        "sns:List*",
                        "cloudwatch:Describe*",
                        "cloudwatch:Get*",
                        "cloudwatch:List*",
                        "logs:Describe*",
                        "logs:Get*",
                        "logs:List*",
                        "logs:StartQuery",
                        "logs:StopQuery",
                        "logs:TestMetricFilter",
                        "logs:FilterLogEvents",
                        "events:DescribeRule",
                        "events:ListRuleNamesByTarget",
                        "events:ListRules",
                        "events:ListTargetsByRule",
                        "events:TestEventPattern",
                        "events:DescribeEventBus",
                        "config:Get*",
                        "config:Describe*",
                        "config:Deliver*",
                        "config:List*",
                        "config:Select*",
                        "tag:GetResources",
                        "tag:GetTagKeys",
                        "cloudtrail:GetTrail",
                        "cloudtrail:GetTrailStatus",
                        "cloudtrail:DescribeTrails",
                        "cloudtrail:ListTrails",
                        "cloudtrail:LookupEvents",
                        "cloudtrail:ListTags",
                        "cloudtrail:ListPublicKeys",
                        "cloudtrail:GetEventSelectors",
                        "cloudtrail:GetInsightSelectors",
                        "s3:GetObject",
                        "s3:GetBucketLocation",
                        "s3:ListAllMyBuckets",
                        "kms:ListAliases",
                        "lambda:ListFunctions",
                        "guardduty:Get*",
                        "guardduty:List*",
                        "redshift:Describe*",
                        "redshift:ViewQueriesInConsole",
                        "elasticmapreduce:Describe*",
                        "elasticmapreduce:List*",
                        "elasticmapreduce:ViewEventsFromAllClustersInConsole",
                        "sdb:Select",
                        "sagemaker:Describe*",
                        "sagemaker:List*",
                        "sagemaker:BatchGetMetrics",
                        "sagemaker:GetSearchSuggestions",
                        "sagemaker:Search"
                    ],
                    resources=["*"]
                ),
                iam.PolicyStatement(
                    actions=[
                        "ec2:StartInstances",
                        "ec2:StopInstances"
                    ],
                    resources=["*"]
                )
            ]
        )
        system_admin_role.add_managed_policy(system_admin_role_policy)

        # S3管理ロール
        s3_admin_role = iam.Role(
            self, 'S3AdminRole',
            role_name='S3AdminRole',
            assumed_by=iam.AccountRootPrincipal()
        )
        s3_admin_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3FullAccess'))
        s3_admin_role_policy = iam.ManagedPolicy(
            self, 'S3AdminRolePolicy',
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.DENY,
                    actions=[
                        "s3:PutAccountPublicAccessBlock",
                        "s3:PutBucketPublicAccessBlock",
                        "s3:PutAccessPointPolicy"
                    ],
                    resources=["*"]
                )
            ]
        )
        s3_admin_role.add_managed_policy(s3_admin_role_policy)

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
                        "sns:Get*",
                        "sns:List*",
                        "cloudwatch:Describe*",
                        "cloudwatch:Get*",
                        "cloudwatch:List*",
                        "logs:Describe*",
                        "logs:Get*",
                        "logs:List*",
                        "logs:StartQuery",
                        "logs:StopQuery",
                        "logs:TestMetricFilter",
                        "logs:FilterLogEvents",
                        "events:DescribeRule",
                        "events:ListRuleNamesByTarget",
                        "events:ListRules",
                        "events:ListTargetsByRule",
                        "events:TestEventPattern",
                        "events:DescribeEventBus",
                        "config:Get*",
                        "config:Describe*",
                        "config:Deliver*",
                        "config:List*",
                        "config:Select*",
                        "tag:GetResources",
                        "tag:GetTagKeys",
                        "cloudtrail:GetTrail",
                        "cloudtrail:GetTrailStatus",
                        "cloudtrail:DescribeTrails",
                        "cloudtrail:ListTrails",
                        "cloudtrail:LookupEvents",
                        "cloudtrail:ListTags",
                        "cloudtrail:ListPublicKeys",
                        "cloudtrail:GetEventSelectors",
                        "cloudtrail:GetInsightSelectors",
                        "s3:GetObject",
                        "s3:GetBucketLocation",
                        "s3:ListAllMyBuckets",
                        "kms:ListAliases",
                        "lambda:ListFunctions",
                        "guardduty:Get*",
                        "guardduty:List*"
                    ],
                    resources=["*"]
                ),
                iam.PolicyStatement(
                    actions=[
                        "s3:GetObject*",
                        "s3:GetBucket*",
                        "s3:List*"
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
        kms_admin_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AWSKeyManagementServicePowerUser'))

        # 分析ロール作成
        data_scientist_role = iam.Role(
            self, 'DataScientistRole',
            role_name='DataScientistRole',
            assumed_by=iam.AccountRootPrincipal()
        )
        data_scientist_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonRedshiftFullAccess'))
        data_scientist_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSageMakerFullAccess'))
        data_scientist_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonElasticMapReduceFullAccess'))
        data_scientist_role_policy = iam.ManagedPolicy(
            self, 'DataScientistRolePolicy',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "quicksight:*"
                    ],
                    resources=["*"]
                )
            ]
        )
        data_scientist_role.add_managed_policy(data_scientist_role_policy)

        # Redshiftクラスター用IAMロール
        redshift_cluster_role = iam.Role(
            self, 'RedshiftClusterRole',
            role_name='RedshiftClusterRole',
            assumed_by=iam.ServicePrincipal('redshift.amazonaws.com')
        )
        redshift_cluster_role_policy = iam.ManagedPolicy(
            self, 'RedshiftClusterRolePolicy',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "s3:*"
                    ],
                    not_resources=[
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
        redshift_cluster_role.add_managed_policy(redshift_cluster_role_policy)

        # ノートブック実行用のIAMロール
        notebook_execution_role = iam.Role(
            self, 'NotebookExecutionRole',
            role_name='NotebookExecutionRole',
            assumed_by=iam.ServicePrincipal('sagemaker.amazonaws.com')
        )
        notebook_execution_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSageMakerFullAccess'))
        notebook_execution_role_policy = iam.ManagedPolicy(
            self, 'NotebookExecutionRolePolicy',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "s3:ListBucket",
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject"
                    ],
                    not_resources=[
                        'arn:aws:s3:::sagemaker-{}-{}'.format(
                            self.node.try_get_context('account'),
                            self.node.try_get_context('bucket_suffix')
                        ),
                        'arn:aws:s3:::sagemaker-{}-{}/*'.format(
                            self.node.try_get_context('account'),
                            self.node.try_get_context('bucket_suffix')
                        ),
                    ]
                ),
            ]
        )
        notebook_execution_role.add_managed_policy(notebook_execution_role_policy)

        ################
        # IAMグループの作成
        ################

        # 全体管理者グループ
        # 全体管理ロールを含む全てのロールにスイッチ可能
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
                        admin_role.role_arn,
                        cost_admin_role.role_arn,
                        system_admin_role.role_arn,
                        s3_admin_role.role_arn,
                        security_audit_role.role_arn,
                        kms_admin_role.role_arn,
                        data_scientist_role.role_arn
                    ]
                )
            ]
        )
        admin_group.add_managed_policy(admin_group_policy)

        # 環境管理者グループ
        # コスト管理ロール、システム管理ロール、S3管理ロールにスイッチ可能
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
                        cost_admin_role.role_arn,
                        system_admin_role.role_arn,
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
        # カスタマー管理ポリシーを全てのグループにアタッチ
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
                            'aws:SourceIp': self.node.try_get_context('allow_ips')
                        }
                    }
                )
            ]
        )
        # カスタマー管理ポリシーをすべてのグループにアタッチ
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
        self.output_props['redshift_cluster_role'] = redshift_cluster_role
        self.output_props['notebook_execution_role'] = notebook_execution_role

    @property
    def outputs(self):
        return self.output_props
