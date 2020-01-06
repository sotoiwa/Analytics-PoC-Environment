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
        # グループの作成
        ################

        # 全体管理者グループ
        admin_group = iam.Group(
            self, 'AdminGroup',
            group_name='AdminGroup'
        )
        admin_group.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AdministratorAccess'))

        # システム管理者グループ
        # コスト管理、S3管理、環境管理のロールを兼ねるグループ
        system_admin_group = iam.Group(
            self, 'SystemAdminGroup',
            group_name='SystemAdminGroup'
        )
        # コスト管理用のインラインポリシー
        billing_admin_policy = iam.Policy(
            self, 'BillingAdminPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "aws-portal:*Billing",
                        "awsbillingconsole:*Billing",
                        "aws-portal:*Usage",
                        "awsbillingconsole:*Usage",
                        "aws-portal:*PaymentMethods",
                        "awsbillingconsole:*PaymentMethods",
                        "budgets:ViewBudget",
                        "budgets:ModifyBudget",
                        "cur:*"
                    ],
                    resources=["*"]
                )
            ]
        )
        billing_admin_policy.attach_to_group(system_admin_group)
        # S3管理用のインラインポリシー
        s3_admin_policy = iam.Policy(
            self, 'S3AdminPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=["s3:*"],
                    resources=["*"]
                )
            ]
        )
        s3_admin_policy.attach_to_group(system_admin_group)
        # 環境管理用のインラインポリシー
        environment_admin_policy = iam.Policy(
            self, 'EnvironmentAdminPolicy',
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
        environment_admin_policy.attach_to_group(system_admin_group)

        # セキュリティ監査者グループ
        # セキュリティ監査とKMS管理のロールを兼ねるグループ
        security_audit_group = iam.Group(
            self, 'SecurityAuditGroup',
            group_name='SecurityAuditGroup'
        )
        # セキュリティ監査者用のインラインポリシー
        system_admin_policy = iam.Policy(
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
                ),
                iam.PolicyStatement(
                    actions=[
                        "s3:GetAccessPoint",
                        "s3:GetLifecycleConfiguration",
                        "s3:GetBucketTagging",
                        "s3:GetInventoryConfiguration",
                        "s3:GetObjectVersionTagging",
                        "s3:ListBucketVersions",
                        "s3:GetBucketLogging",
                        "s3:ListBucket",
                        "s3:GetAccelerateConfiguration",
                        "s3:GetBucketPolicy",
                        "s3:GetObjectVersionTorrent",
                        "s3:GetObjectAcl",
                        "s3:GetEncryptionConfiguration",
                        "s3:GetBucketObjectLockConfiguration",
                        "s3:GetBucketRequestPayment",
                        "s3:GetAccessPointPolicyStatus",
                        "s3:GetObjectVersionAcl",
                        "s3:GetObjectTagging",
                        "s3:GetMetricsConfiguration",
                        "s3:HeadBucket",
                        "s3:GetBucketPublicAccessBlock",
                        "s3:GetBucketPolicyStatus",
                        "s3:ListBucketMultipartUploads",
                        "s3:GetObjectRetention",
                        "s3:GetBucketWebsite",
                        "s3:ListAccessPoints",
                        "s3:ListJobs",
                        "s3:GetBucketVersioning",
                        "s3:GetBucketAcl",
                        "s3:GetObjectLegalHold",
                        "s3:GetBucketNotification",
                        "s3:GetReplicationConfiguration",
                        "s3:ListMultipartUploadParts",
                        "s3:GetObject",
                        "s3:GetObjectTorrent",
                        "s3:GetAccountPublicAccessBlock",
                        "s3:ListAllMyBuckets",
                        "s3:DescribeJob",
                        "s3:GetBucketCORS",
                        "s3:GetAnalyticsConfiguration",
                        "s3:GetObjectVersionForReplication",
                        "s3:GetBucketLocation",
                        "s3:GetAccessPointPolicy",
                        "s3:GetObjectVersion"
                    ],
                    resources=["*"]
                ),
            ]
        )
        system_admin_policy.attach_to_group(security_audit_group)
        # KMS管理用のポリシー
        kms_admin_policy = iam.Policy(
            self, 'KmsAdminPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=["kms:*"],
                    resources=["*"]
                )
            ]
        )
        kms_admin_policy.attach_to_role(security_audit_group)

        # 分析者グループ
        data_scientist_group = iam.Group(
            self, 'DataScientistGroup',
            group_name='DataScientistGroup'
        )
        # 分析者用のインラインポリシー
        data_scientist_policy = iam.Policy(
            self, 'DataScientistPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "ec2:*",
                        "redshift:*",
                        "elasticmapreduce:*",
                        "sagemaker:*",
                        "quicksight:*"
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
                )
            ]
        )
        data_scientist_policy.attach_to_group(data_scientist_group)

        ################
        # IPアドレス制限
        ################

        # IPアドレス制限を行う管理ポリシー
        ip_address_policy = iam.ManagedPolicy(
            self, 'IpAddressPolicy',
            managed_policy_name='IpAddressPolicy',
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.DENY,
                    actions=['*'],
                    resources=['*'],
                    conditions={
                        'NotIpAddress': {
                            'aws:SourceIp': [
                                '0.0.0.0/0'
                            ]
                        }
                    }
                )
            ]
        )

        # ポリシーをグループにアタッチ
        # ip_address_policy.attach_to_group(admin_group)
        ip_address_policy.attach_to_group(system_admin_group)
        ip_address_policy.attach_to_group(security_audit_group)
        ip_address_policy.attach_to_group(data_scientist_group)

        ################
        # ユーザーの作成
        ################

        # 作成したユーザーのパスワードはSecretManagerに格納する

        # 全体管理者ユーザーの作成
        admin_user_names = ['admin-user']
        for user_name in admin_user_names:
            secret = secretsmanager.Secret(self, '{}-Secrets'.format(user_name))
            user = iam.User(
                self, user_name,
                user_name=user_name,
                password=secret.secret_value,
                password_reset_required=True
            )
            user.add_to_group(admin_group)

        # システム管理者ユーザーの作成
        system_admin_user_names = ['system-admin-user']
        for user_name in system_admin_user_names:
            secret = secretsmanager.Secret(self, '{}-Secrets'.format(user_name))
            user = iam.User(
                self, user_name,
                user_name=user_name,
                password=secret.secret_value,
                password_reset_required=True
            )
            user.add_to_group(system_admin_group)

        # セキュリティー監査ユーザーの作成
        security_audit_user_names = ['security-audit-user']
        for user_name in security_audit_user_names:
            secret = secretsmanager.Secret(self, '{}-Secrets'.format(user_name))
            user = iam.User(
                self, user_name,
                user_name=user_name,
                password=secret.secret_value,
                password_reset_required=True
            )
            user.add_to_group(security_audit_group)

        # 分析者ユーザーの作成
        data_scientist_user_names = ['data-user']
        for user_name in data_scientist_user_names:
            secret = secretsmanager.Secret(self, '{}-Secrets'.format(user_name))
            user = iam.User(
                self, user_name,
                user_name=user_name,
                password=secret.secret_value,
                password_reset_required=True
            )
            user.add_to_group(data_scientist_group)

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
