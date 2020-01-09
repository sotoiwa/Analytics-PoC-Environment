from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    aws_redshift as redshift
)


class RedShiftStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = props['analytics_vpc']

        # 参考リンク
        # https://aws.amazon.com/jp/blogs/news/automate-amazon-redshift-cluster-creation-using-aws-cloudformation/
        # https://aws.amazon.com/jp/blogs/news/build-fast-flexible-secure-machine-learning-platform-using-amazon-sagemaker-and-amazon-redshift/

        # IAMロール
        redshift_role = iam.Role(
            self, 'RedShiftRole',
            assumed_by=iam.ServicePrincipal('redshift.amazonaws.com')
        )

        # セキュリティーグループ
        redshift_sg = ec2.SecurityGroup(
            self, 'RedShiftSg',
            vpc=vpc
        )

        # ログ用のバケット

        # バケットポリシー

        # クラスターパラメーターグループ
        cluster_parameter_group = redshift.CfnClusterParameterGroup(
            self, 'RedShiftClusterParameterGroup',
            description='RedShift Cluster parameter group',
            parameter_group_family='redshift-1.0',
            parameters=None
        )

        # クラスターサブネットグループ
        cluster_subnet_group = redshift.CfnClusterSubnetGroup(
            self, 'RedShiftClusterSubnetGroup',
            description='RedShift Cluster subnet group',
            subnet_ids=vpc.select_subnets(subnet_type=ec2.SubnetType.ISOLATED).subnet_ids
        )

        # クラスター
        cluster = redshift.CfnCluster(
            self, 'RedShiftCluster',
            cluster_type='multi-node',
            number_of_nodes=2,
            node_type='dc2.large',
            cluster_identifier='redshift-cluster',
            db_name='dev',
            port=5439,
            master_username='awsuser',
            master_user_password=self.node.try_get_context('redshift')['master_user_password'],
            iam_roles=[redshift_role.role_arn],
            vpc_security_group_ids=[redshift_sg.security_group_id],
            cluster_subnet_group_name=cluster_subnet_group.ref,
            cluster_parameter_group_name=cluster_parameter_group.ref,
            publicly_accessible=False,
            allow_version_upgrade=True,
            automated_snapshot_retention_period=8,
            encrypted=False,
            logging_properties=None
        )

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
