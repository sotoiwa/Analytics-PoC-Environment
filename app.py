#!/usr/bin/env python3

from aws_cdk import core

from cdksample.workspaces_vpc_stack import WorkSpacesVpcStack
from cdksample.analytics_vpc_stack import AnalyticsVpcStack
from cdksample.sap_vpc_stack import SapVpcStack
from cdksample.vpc_peering_stack import VpcPeeringStack
from cdksample.audit_log_stack import AuditLogStack
from cdksample.iam_stack import IamStack
from cdksample.bucket_stack import BucketStack
from cdksample.proxy_stack import ProxyStack
from cdksample.redshift_stack import RedShiftStack

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

audit_log_stack = AuditLogStack(app, '{}-AuditLogStack'.format(props['prefix']), env=env, props=props)
props = audit_log_stack.outputs

iam_stack = IamStack(app, '{}-IamStack'.format(props['prefix']), env=env, props=props)
props = iam_stack.outputs

bucket_stack = BucketStack(app, '{}-BucketStack'.format(props['prefix']), env=env, props=props)
props = bucket_stack.outputs

proxy_stack = ProxyStack(app, '{}-ProxyStack'.format(props['prefix']), env=env, props=props)
props = proxy_stack.outputs

redshift_stack = RedShiftStack(app, '{}-RedShiftStack'.format(props['prefix']), env=env, props=props)
props = redshift_stack.outputs

app.synth()
