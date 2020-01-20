from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_sagemaker as sagemaker
)


class SageMakerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = props['analytics_vpc']

        # 参考リンク
        # https://aws.amazon.com/jp/blogs/news/build-fast-flexible-secure-machine-learning-platform-using-amazon-sagemaker-and-amazon-redshift/

        # IAMロール
        notebook_execution_role = iam.Role(
            self, 'NotebookExecutionRole',
            assumed_by=iam.ServicePrincipal('sagemaker.amazonaws.com')
        )

        # セキュリティーグループ
        notebook_sg = ec2.SecurityGroup(
            self, 'NotebookSecurityGroup',
            vpc=vpc
        )

        # Notebookインスタンス
        for i in range(self.node.try_get_context('sagemaker')['number_of_notebooks']):
            notebook_instance = sagemaker.CfnNotebookInstance(
                self, 'NotebookInstance{}'.format(i + 1),
                instance_type=self.node.try_get_context('sagemaker')['instance_type'],
                notebook_instance_name='{}{}'.format(
                    self.node.try_get_context('sagemaker')['notebook_instance_name'], i + 1),
                subnet_id=vpc.select_subnets(subnet_type=ec2.SubnetType.ISOLATED).subnet_ids[i % 2],
                security_group_ids=[notebook_sg.security_group_id],
                role_arn=notebook_execution_role.role_arn,
                direct_internet_access='Disabled'
            )

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
