from aws_cdk import (
    core,
    aws_iam as iam,
    aws_kms as kms,
    aws_s3 as s3
)


class BucketStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        admin_role = props['admin_role']
        cost_admin_role = props['cost_admin_role']
        s3_admin_role = props['s3_admin_role']
        system_admin_role = props['system_admin_role']
        security_audit_role = props['security_audit_role']
        kms_admin_role = props['kms_admin_role']
        data_scientist_role = props['data_scientist_role']

        ################
        # キーの作成
        ################

        # キーを作成
        customer_key = kms.Key(
            self, 'CustomerKey',
            enable_key_rotation=True,
            alias='CustomerKey'
        )

        # キーポリシーを設定する
        customer_key.add_to_resource_policy(
            statement=iam.PolicyStatement(
                principals=[
                    iam.ArnPrincipal('arn:aws:iam::{}:role/AdminRole'.format(
                        self.node.try_get_context('account'))),
                    iam.ArnPrincipal('arn:aws:iam::{}:role/S3AdminRole'.format(
                        self.node.try_get_context('account'))),
                    iam.ArnPrincipal('arn:aws:iam::{}:role/SystemAdminRole'.format(
                        self.node.try_get_context('account'))),
                    iam.ArnPrincipal('arn:aws:iam::{}:role/DataScientistRole'.format(
                        self.node.try_get_context('account')))
                ],
                actions=[
                    "kms:Decrypt",
                    "kms:DescribeKey",
                    "kms:Encrypt",
                    "kms:ReEncrypt*",
                    "kms:GenerateDataKey*"
                ],
                resources=['*']
            )
        )

        # キーを使った暗号化・復号を許可するIAMポリシー
        customer_key_encrypt_decrypt_policy = iam.ManagedPolicy(
            self, 'CustomerKeyEncryptDecryptPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "kms:Decrypt",
                        "kms:DescribeKey",
                        "kms:Encrypt",
                        "kms:ReEncrypt*",
                        "kms:GenerateDataKey*"
                    ],
                    resources=[customer_key.key_arn]
                )
            ]
        )

        for role in [admin_role, s3_admin_role, system_admin_role, data_scientist_role]:
            customer_key_encrypt_decrypt_policy.attach_to_role(role)

        ################
        # データ用バケットの作成
        ################

        # データ用のS3バケット
        data_bucket = s3.Bucket(
            self, 'DataBucket',
            bucket_name='data-{}-{}'.format(
                self.node.try_get_context('account'),
                self.node.try_get_context('bucket_suffix'),
            ),
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=customer_key,
            versioned=True
        )
        # いくつかのIAMロールからの参照を許可するバケットポリシー
        data_bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                principals=[
                    iam.ArnPrincipal('arn:aws:iam::{}:role/AdminRole'.format(
                        self.node.try_get_context('account'))),
                    iam.ArnPrincipal('arn:aws:iam::{}:role/S3AdminRole'.format(
                        self.node.try_get_context('account'))),
                    iam.ArnPrincipal('arn:aws:iam::{}:role/SystemAdminRole'.format(
                        self.node.try_get_context('account'))),
                    iam.ArnPrincipal('arn:aws:iam::{}:role/DataScientistRole'.format(
                        self.node.try_get_context('account')))
                ],
                actions=[
                    "s3:GetObject*",
                    "s3:GetBucket*",
                    "s3:List*",
                    "s3:DeleteObject*",
                    "s3:PutObject*",
                    "s3:Abort*"
                ],
                resources=[
                    data_bucket.bucket_arn,
                    data_bucket.arn_for_objects('*')
                ]
            )
        )

        ################
        # ログ用バケットの作成
        ################

        # ログ格納用のS3バケット
        log_bucket = s3.Bucket(
            self, 'LogBucket',
            bucket_name='log-{}-{}'.format(
                self.node.try_get_context('account'),
                self.node.try_get_context('bucket_suffix'),
            ),
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        # Redshiftからの書き込みを許可するバケットポリシー
        # https://docs.aws.amazon.com/ja_jp/redshift/latest/mgmt/db-auditing.html#db-auditing-manage-log-files
        redshift_logging_account_map = {
            'us-east-1': '193672423079',
            'us-east-2': '391106570357',
            'us-west-1': '262260360010',
            'us-west-2': '902366379725',
            'ap-east-1': '313564881002',
            'ap-south-1': '865932855811',
            'ap-northeast-3': '090321488786',
            'ap-northeast-2': '760740231472',
            'ap-southeast-1': '361669875840',
            'ap-southeast-2': '762762565011',
            'ap-northeast-1': '404641285394',
            'ca-central-1': '907379612154',
            'eu-central-1': '053454850223',
            'eu-west-1': '210876761215',
            'eu-west-2': '307160386991',
            'eu-west-3': '915173422425',
            'eu-north-1': '729911121831',
            'me-south-1': '013126148197',
            'sa-east-1': '075028567923'
        }
        log_bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                principals=[
                    iam.ArnPrincipal('arn:aws:iam::{}:user/logs'.format(
                        redshift_logging_account_map[self.node.try_get_context('region')]))
                ],
                actions=[
                    "s3:PutObject"
                ],
                resources=[
                    log_bucket.arn_for_objects('*')
                ]
            )
        )
        log_bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                principals=[
                    iam.ArnPrincipal('arn:aws:iam::{}:user/logs'.format(
                        redshift_logging_account_map[self.node.try_get_context('region')]))
                ],
                actions=[
                    "s3:GetBucketAcl"
                ],
                resources=[
                    log_bucket.bucket_arn
                ]
            )
        )

        # VPCフローログ、CloudTrail、Config用からの書き込みを許可するバケットポリシーを明示的に設定する
        log_bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                principals=[
                    iam.ServicePrincipal('delivery.logs.amazonaws.com'),
                    iam.ServicePrincipal('cloudtrail.amazonaws.com'),
                    iam.ServicePrincipal('config.amazonaws.com')
                ],
                actions=[
                    "s3:PutObject"
                ],
                resources=[
                    log_bucket.arn_for_objects("AWSLogs/{}/*".format(self.node.try_get_context('account')))
                ],
                conditions={
                    "StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}
                }
            )
        )
        log_bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                principals=[
                    iam.ServicePrincipal('delivery.logs.amazonaws.com'),
                    iam.ServicePrincipal('cloudtrail.amazonaws.com'),
                    iam.ServicePrincipal('config.amazonaws.com')
                ],
                actions=[
                    "s3:GetBucketAcl"
                ],
                resources=[
                    log_bucket.bucket_arn
                ]
            )
        )

        # いくつかのIAMロールからの参照を許可するバケットポリシー
        log_bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                principals=[
                    iam.ArnPrincipal('arn:aws:iam::{}:role/AdminRole'.format(
                        self.node.try_get_context('account'))),
                    iam.ArnPrincipal('arn:aws:iam::{}:role/SecurityAuditRole'.format(
                        self.node.try_get_context('account')))
                ],
                actions=[
                    "s3:GetObject*",
                    "s3:GetBucket*",
                    "s3:List*"
                ],
                resources=[
                    log_bucket.bucket_arn,
                    log_bucket.arn_for_objects('*')
                ]
            )
        )

        self.output_props = props.copy()
        self.output_props['customer_key'] = customer_key
        self.output_props['data_bucket'] = data_bucket
        self.output_props['log_bucket'] = log_bucket

    @property
    def outputs(self):
        return self.output_props
