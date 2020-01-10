from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_iam as iam,
    aws_kms as kms
)


class BucketStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        admin_group = props['admin_group']
        environment_admin_group = props['environment_admin_group']
        data_scientist_group = props['data_scientist_group']
        data_key_encrypt_decrypt_users = props['data_key_encrypt_decrypt_users']
        data_bucket_read_write_users = props['data_bucket_read_write_users']

        ################
        # キーの作成
        ################

        # キーを作成
        data_key = kms.Key(
            self, 'DataKey',
            enable_key_rotation=True,
            alias='data'
        )

        # キーを使って暗号化・復号できるカスタマー管理ポリシー
        data_key_encrypt_decrypt_policy = iam.ManagedPolicy(
            self, 'DataKeyEncryptDecryptPolicy',
            managed_policy_name='DataKeyEncryptDecryptPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        "kms:Decrypt",
                        "kms:DescribeKey",
                        "kms:Encrypt",
                        "kms:ReEncrypt*",
                        "kms:GenerateDataKey*"
                    ],
                    resources=[data_key.key_arn]
                )
            ]
        )
        # カスタマー管理ポリシーをグループにアタッチ
        for group in [admin_group, environment_admin_group, data_scientist_group]:
            data_key_encrypt_decrypt_policy.attach_to_group(group)

        # キーポリシーを設定する
        # IAMグループを指定できないのでIAMユーザーを指定する
        data_key.add_to_resource_policy(
            statement=iam.PolicyStatement(
                principals=data_key_encrypt_decrypt_users,
                actions=[
                    "kms:Decrypt",
                    "kms:DescribeKey",
                    "kms:Encrypt",
                    "kms:ReEncrypt*",
                    "kms:GenerateDataKey*"
                ],
                resources=["*"]
            )
        )

        ################
        # データ用のバケットの作成
        ################

        # データ用のS3バケット
        data_bucket = s3.Bucket(
            self, 'DataBucket',
            bucket_name='data-{}'.format(self.node.try_get_context('account')),
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=data_key
        )

        # バケットポリシーを設定する
        # IAMグループを指定できないのでIAMユーザーを指定する
        data_bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                principals=data_bucket_read_write_users,
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
                    data_bucket.arn_for_objects("*")
                ]
            )
        )

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
