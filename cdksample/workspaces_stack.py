from aws_cdk import (
    core,
    aws_directoryservice as directoryservice
)


class WorkSpacesStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # SimpleADの作成
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_directoryservice/CfnSimpleAD.html

        # simple_ad = directoryservice.CfnSimpleAD(
        #     self, 'SimpleAD',
        #     name='sotosugicorp.example.com',
        #     password='hogehoge',
        #     size='Small',
        #     vpc_settings={
        #         'VpcId':  vpc,
        #         'SubnetIds':
        #     }
        #
        # )

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
