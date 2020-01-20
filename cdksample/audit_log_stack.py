from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_iam as iam,
    aws_cloudtrail as cloudtrail
)


class AuditLogStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        workspaces_vpc = props['workspaces_vpc']
        analytics_vpc = props['analytics_vpc']
        sap_vpc = props['sap_vpc']
        log_bucket_read_users = props['log_bucket_read_users']

        # ログ格納用のS3バケット
        log_bucket = s3.Bucket(
            self, 'LogBucket',
            bucket_name='log-{}-{}'.format(
                self.node.try_get_context('account'),
                self.node.try_get_context('bucket_suffix'),
            ),
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL
        )

        # VPC FlowLogsを有効化
        for vpc in [workspaces_vpc, analytics_vpc, sap_vpc]:
            flowlogs = ec2.CfnFlowLog(
                self, 'FlowLogs{}'.format(vpc.to_string()),
                resource_id=vpc.vpc_id,
                resource_type='VPC',
                traffic_type='ALL',
                log_destination_type='s3',
                log_destination=log_bucket.bucket_arn
            )

        # CloudTrailの有効化
        trail = cloudtrail.Trail(
            self, 'CloudTrail',
            bucket=log_bucket,
            enable_file_validation=True,
            send_to_cloud_watch_logs=True
        )

        # VPCフローログ用のバケットポリシーを設定する
        # IAMユーザー向けのポリシーを追加すると消えてしまった（バグ？）ので明示的に追加している
        log_bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                principals=[
                    iam.ServicePrincipal('delivery.logs.amazonaws.com')
                ],
                actions=[
                    "s3:PutObject"
                ],
                resources=[
                    log_bucket.arn_for_objects("AWSLogs/{}/*".format(self.node.try_get_context('account')))
                ],
                conditions={"StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}}
            )
        )
        log_bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                principals=[
                    iam.ServicePrincipal('delivery.logs.amazonaws.com')
                ],
                actions=[
                    "s3:GetBucketAcl"
                ],
                resources=[
                    log_bucket.bucket_arn
                ]
            )
        )

        # RedShift用のバケットポリシーの追加
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

        # バケットポリシーを設定する
        # IAMグループを指定できないのでIAMユーザーを指定する
        log_bucket.add_to_resource_policy(
            permission=iam.PolicyStatement(
                principals=log_bucket_read_users,
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
        self.output_props['log_bucket'] = log_bucket

    @property
    def outputs(self):
        return self.output_props
