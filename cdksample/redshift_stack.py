from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_redshift as redshift
)


class RedShiftStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # 参考リンク
        # https://aws.amazon.com/jp/blogs/news/automate-amazon-redshift-cluster-creation-using-aws-cloudformation/

        # IAMロール
        redshift_role = iam.Role(
            self, 'RedShiftRole',
        )

        # セキュリティーグループ

        redshift_cluster = redshift.CfnCluster(
            self, 'RedShiftCluster',
            cluster_type='multi-node',
            number_of_nodes=2
        )



        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
