from aws_cdk import (
    core,
    aws_iam as iam,
    aws_s3 as s3,
    aws_secretsmanager as secretsmanager
)


class TestStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # テスト用のS3バケット
        test_bucket = s3.Bucket(
            self, 'TestBucket',
            bucket_name='test-{}-{}'.format(
                self.node.try_get_context('account'),
                self.node.try_get_context('bucket_suffix'),
            ),
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        # テスト用のユーザー
        secret = secretsmanager.Secret(self, '{}-Secrets'.format('test-user'))
        test_user = iam.User(
            self, 'TestUser',
            user_name='test-user',
            password=secret.secret_value,
            password_reset_required=True
        )
        test_bucket.grant_read(test_user)

        test_bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                principals=[
                    iam.ArnPrincipal('arn:aws:iam::448772462142:user/security-audit-user')
                ],
                actions=[
                    "s3:GetBucketAcl"
                ],
                resources=[
                    test_bucket.bucket_arn
                ]
            )
        )

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
