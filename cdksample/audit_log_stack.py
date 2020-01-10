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
            bucket_name='log-{}'.format(self.node.try_get_context('account')),
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
                    log_bucket.arn_for_objects("*")
                ]
            )
        )

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
