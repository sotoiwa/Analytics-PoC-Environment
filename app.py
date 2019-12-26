#!/usr/bin/env python3

from aws_cdk import core

from cdksample.workspaces_vpc_stack import WorkSpacesVpcStack
from cdksample.analytics_vpc_stack import AnalyticsVpcStack
from cdksample.sap_vpc_stack import SapVpcStack
from cdksample.vpc_peering_stack import VpcPeeringStack
from cdksample.iam_stack import IamStack
from cdksample.basion_stack import BasionStack
from cdksample.proxy_stack import ProxyStack

app = core.App()

props = {
    'prefix': 'Sample'
}

env = core.Environment(
    account=app.node.try_get_context('account'),
    region=app.node.try_get_context('region')
)

workspaces_vpc_stack = WorkSpacesVpcStack(app, '{}-WorkSpacesVpcStack'.format(props['prefix']), env=env, props=props)
props = workspaces_vpc_stack.outputs

analytics_vpc_stack = AnalyticsVpcStack(app, '{}-AnalyticsVpcStack'.format(props['prefix']), env=env, props=props)
props = analytics_vpc_stack.outputs

sap_vpc_stack = SapVpcStack(app, '{}-SapVpcStack'.format(props['prefix']), env=env, props=props)
props = sap_vpc_stack.outputs

vpc_peering_stack = VpcPeeringStack(app, '{}-VpcPeeringStack'.format(props['prefix']), env=env, props=props)
props = vpc_peering_stack.outputs

iam_stack = IamStack(app, '{}-IamStack'.format(props['prefix']), env=env, props=props)
props = iam_stack.outputs

basion_stack = BasionStack(app, '{}-BasionStack'.format(props['prefix']), env=env, props=props)
props = basion_stack.outputs

proxy_stack = ProxyStack(app, '{}-ProxyStack'.format(props['prefix']), env=env, props=props)
props = proxy_stack.outputs

app.synth()
