from aws_cdk import (
    core,
    aws_ec2 as ec2
)


class BastionStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = props['workspaces_vpc']
        bastion_sg = props['bastion_sg']

        # EC2の作成
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/Instance.html

        # Bastion用EC2ホスト
        bastion_host = ec2.Instance(
            self, 'BasionHost',
            instance_type=ec2.InstanceType('t2.small'),
            machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
            key_name=self.node.try_get_context('key_name'),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=bastion_sg
        )

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
