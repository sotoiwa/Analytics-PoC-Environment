#!/usr/bin/env python3

from aws_cdk import core

from cdksample.network_stack import NetworkStack
from cdksample.iam_stack import IamStack
from cdksample.bucket_stack import BucketStack
from cdksample.audit_log_stack import AuditLogStack
from cdksample.events_stack import EventsStack
from cdksample.global_events_stack import GlobalEventsStack
from cdksample.config_stack import ConfigStack
from cdksample.proxy_stack import ProxyStack
from cdksample.bastion_stack import BastionStack
from cdksample.redshift_stack import RedshiftStack
from cdksample.sagemaker_stack import SageMakerStack


app = core.App()
prefix = app.node.try_get_context('stack_prefix')
env = core.Environment(
    account=app.node.try_get_context('account'),
    region=app.node.try_get_context('region')
)
global_env = core.Environment(
    account=app.node.try_get_context('account'),
    region='us-east-1'
)
props = dict()

network_stack = NetworkStack(app, '{}-NetworkStack'.format(prefix), env=env, props=props)
props = network_stack.outputs

iam_stack = IamStack(app, '{}-IamStack'.format(prefix), env=env, props=props)
props = iam_stack.outputs

bucket_stack = BucketStack(app, '{}-BucketStack'.format(prefix), env=env, props=props)
props = bucket_stack.outputs

audit_log_stack = AuditLogStack(app, '{}-AuditLogStack'.format(prefix), env=env, props=props)
props = audit_log_stack.outputs

events_stack = EventsStack(app, '{}-EventsStack'.format(prefix), env=env, props=props)
props = events_stack.outputs

global_events_stack = GlobalEventsStack(app, '{}-GlobalEventsStack'.format(prefix), env=global_env, props=props)
props = global_events_stack.outputs

config_stack = ConfigStack(app, '{}-ConfigStack'.format(prefix), env=env, props=props)
props = config_stack.outputs

proxy_stack = ProxyStack(app, '{}-ProxyStack'.format(prefix), env=env, props=props)
props = proxy_stack.outputs

bastion_stack = BastionStack(app, '{}-BastionStack'.format(prefix), env=env, props=props)
props = bastion_stack.outputs

redshift_stack = RedshiftStack(app, '{}-RedshiftStack'.format(prefix), env=env, props=props)
props = redshift_stack.outputs

sagemaker_stack = SageMakerStack(app, '{}-SageMakerStack'.format(prefix), env=env, props=props)
props = sagemaker_stack.outputs

app.synth()
