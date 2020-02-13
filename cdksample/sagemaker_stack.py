from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_kms as kms,
    aws_s3 as s3,
    aws_sagemaker as sagemaker
)


class SageMakerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = props['analytics_vpc']
        notebook_sg = props['notebook_sg']
        notebook_execution_role = props['notebook_execution_role']
        data_bucket = props['data_bucket']
        customer_key = props['customer_key']

        # 参考リンク
        # https://aws.amazon.com/jp/blogs/news/build-fast-flexible-secure-machine-learning-platform-using-amazon-sagemaker-and-amazon-redshift/

        # Notebookインスタンス
        i = 0
        for notebook_instance_name in self.node.try_get_context('sagemaker')['notebook_instance_names']:
            # インスタンスの作成
            notebook_instance = sagemaker.CfnNotebookInstance(
                self, '{}NotebookInstance'.format(notebook_instance_name),
                instance_type=self.node.try_get_context('sagemaker')['instance_type'],
                notebook_instance_name=notebook_instance_name,
                subnet_id=vpc.select_subnets(subnet_type=ec2.SubnetType.ISOLATED).subnet_ids[i % 2],
                security_group_ids=[notebook_sg.security_group_id],
                role_arn=notebook_execution_role.role_arn,
                direct_internet_access='Disabled',
                kms_key_id=customer_key.key_id,
                volume_size_in_gb=self.node.try_get_context('sagemaker')['volume_size_in_gb']
            )
            i += 1

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
