from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_iam as iam,
    aws_kms as kms
)


class BucketStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        data_key = props['data_key']

        ################
        # バケットの作成
        ################

        # データ格納用のS3バケット
        data_bucket = s3.Bucket(
            self, 'DataBucket',
            bucket_name='data-{}'.format(self.node.try_get_context('account')),
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True
            ),
            encryption=s3.BucketEncryption.KMS,
            encryption_key=data_key
        )

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
