from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_cloudtrail as cloudtrail
)


class AuditLogStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        workspaces_vpc = props['workspaces_vpc']
        analytics_vpc = props['analytics_vpc']
        sap_vpc = props['sap_vpc']

        # ログ格納用のS3バケット
        log_bucket = s3.Bucket(
            self, 'LogBucket',
            bucket_name='log-{}'.format(self.node.try_get_context('account')),
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=True,
                ignore_public_acls=True,
                restrict_public_buckets=True
            )
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

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
