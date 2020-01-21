#!/usr/bin/env python3

from aws_cdk import core

from cdksample.test_stack import TestStack
from cdksample.workspaces_vpc_stack import WorkSpacesVpcStack
from cdksample.analytics_vpc_stack import AnalyticsVpcStack
from cdksample.sap_vpc_stack import SapVpcStack
from cdksample.vpc_peering_stack import VpcPeeringStack
from cdksample.audit_log_stack import AuditLogStack
from cdksample.iam_stack import IamStack
from cdksample.bucket_stack import BucketStack
from cdksample.proxy_stack import ProxyStack
from cdksample.bastion_stack import BastionStack
from cdksample.redshift_stack import RedshiftStack
from cdksample.sagemaker_stack import SageMakerStack
from cdksample.config_stack import ConfigStack
from cdksample.events_stack import EventsStack


app = core.App()
prefix = app.node.try_get_context('stack_prefix')
env = core.Environment(
    account=app.node.try_get_context('account'),
    region=app.node.try_get_context('region')
)
props = dict()

test_stack = TestStack(app, '{}-TestStack'.format(prefix), env=env, props=props)
props = test_stack.outputs

bucket_stack = BucketStack(app, '{}-BucketStack'.format(prefix), env=env, props=props)
props = bucket_stack.outputs

workspaces_vpc_stack = WorkSpacesVpcStack(app, '{}-WorkSpacesVpcStack'.format(prefix), env=env, props=props)
props = workspaces_vpc_stack.outputs

analytics_vpc_stack = AnalyticsVpcStack(app, '{}-AnalyticsVpcStack'.format(prefix), env=env, props=props)
props = analytics_vpc_stack.outputs

sap_vpc_stack = SapVpcStack(app, '{}-SapVpcStack'.format(prefix), env=env, props=props)
props = sap_vpc_stack.outputs

vpc_peering_stack = VpcPeeringStack(app, '{}-VpcPeeringStack'.format(prefix), env=env, props=props)
props = vpc_peering_stack.outputs

audit_log_stack = AuditLogStack(app, '{}-AuditLogStack'.format(prefix), env=env, props=props)
props = audit_log_stack.outputs

iam_stack = IamStack(app, '{}-IamStack'.format(prefix), env=env, props=props)
props = iam_stack.outputs

proxy_stack = ProxyStack(app, '{}-ProxyStack'.format(prefix), env=env, props=props)
props = proxy_stack.outputs

bastion_stack = BastionStack(app, '{}-BastionStack'.format(prefix), env=env, props=props)
props = bastion_stack.outputs

redshift_stack = RedshiftStack(app, '{}-RedshiftStack'.format(prefix), env=env, props=props)
props = redshift_stack.outputs

sagemaker_stack = SageMakerStack(app, '{}-SageMakerStack'.format(prefix), env=env, props=props)
props = sagemaker_stack.outputs

config_stack = ConfigStack(app, '{}-ConfigStack'.format(prefix), env=env, props=props)
props = config_stack.outputs

events_stack = EventsStack(app, '{}-EventsStack'.format(prefix), env=env, props=props)
props = events_stack.outputs

app.synth()
