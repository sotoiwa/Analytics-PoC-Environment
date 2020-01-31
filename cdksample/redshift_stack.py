from aws_cdk import (
    core,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_redshift as redshift
)


class RedshiftStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = props['analytics_vpc']
        redshift_sg = props['redshift_sg']
        redshift_cluster_role = props['redshift_cluster_role']
        customer_key = props['customer_key']

        # 参考リンク
        # https://aws.amazon.com/jp/blogs/news/automate-amazon-redshift-cluster-creation-using-aws-cloudformation/
        # https://aws.amazon.com/jp/blogs/news/build-fast-flexible-secure-machine-learning-platform-using-amazon-sagemaker-and-amazon-redshift/

        # クラスターパラメーターグループ
        cluster_parameter_group = redshift.CfnClusterParameterGroup(
            self, 'RedshiftClusterParameterGroup',
            description='Redshift Cluster parameter group',
            parameter_group_family='redshift-1.0',
            parameters=[
                {
                    "parameterName": "enable_user_activity_logging",
                    "parameterValue": "true",
                }
            ]
        )

        # クラスターサブネットグループ
        cluster_subnet_group = redshift.CfnClusterSubnetGroup(
            self, 'RedshiftClusterSubnetGroup',
            description='Redshift Cluster subnet group',
            subnet_ids=vpc.select_subnets(subnet_type=ec2.SubnetType.ISOLATED).subnet_ids
        )

        # クラスター
        cluster = redshift.CfnCluster(
            self, 'RedshiftCluster',
            cluster_type=self.node.try_get_context('redshift')['cluster_type'],
            number_of_nodes=self.node.try_get_context('redshift')['number_of_nodes'],
            node_type=self.node.try_get_context('redshift')['node_type'],
            cluster_identifier=self.node.try_get_context('redshift')['cluster_identifier'],
            db_name=self.node.try_get_context('redshift')['db_name'],
            port=self.node.try_get_context('redshift')['port'],
            master_username=self.node.try_get_context('redshift')['master_username'],
            master_user_password=self.node.try_get_context('redshift')['master_user_password'],
            iam_roles=[redshift_cluster_role.role_arn],
            vpc_security_group_ids=[redshift_sg.security_group_id],
            cluster_subnet_group_name=cluster_subnet_group.ref,
            cluster_parameter_group_name=cluster_parameter_group.ref,
            publicly_accessible=False,
            allow_version_upgrade=True,
            automated_snapshot_retention_period=self.node.try_get_context('redshift')[
                'automated_snapshot_retention_period'],
            encrypted=True,
            kms_key_id=customer_key.key_id,
            logging_properties={
                "bucketName": "log-{}-{}".format(
                    self.node.try_get_context('account'),
                    self.node.try_get_context('bucket_suffix'),
                ),
                "s3KeyPrefix": "RedshiftLogs"
            }
        )

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
