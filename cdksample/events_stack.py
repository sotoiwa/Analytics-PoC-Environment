from aws_cdk import (
    core,
    aws_events as events,
    aws_events_targets as targets,
    aws_sns as sns,
    aws_iam as iam
)


class EventsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        alert_topic = sns.Topic(
            self, 'AlertTopic',
            topic_name='AlertTopic'
        )
        alert_topic.add_to_resource_policy(
            statement=iam.PolicyStatement(
                principals=[
                    iam.ServicePrincipal('events.amazonaws.com')
                ],
                actions=[
                    "sns:Publish"
                ],
                resources=[
                    alert_topic.topic_arn
                ]
            )
        )

        ec2_event_names = [
            "AttachInternetGateway",
            "AssociateRouteTable",
            "CreateRoute",
            "DeleteCustomerGateway",
            "DeleteInternetGateway",
            "DeleteRoute",
            "DeleteRouteTable",
            "DeleteDhcpOptions",
            "DisassociateRouteTable"
            "RunInstances",
            "CreateInstances",
            "LaunchInstances",
            "TerminateInstances",
            "AuthorizeSecurityGroupIngress",
            "AuthorizeSecurityGroupEgress",
            "RevokeSecurityGroupIngress",
            "RevokeSecurityGroupEgress",
            "CreateSecurityGroup",
            "DeleteSecurityGroup"
        ]

        for event_name in ec2_event_names:
            ec2_rule = events.Rule(
                self, 'Ec2{}Rule'.format(event_name),
                event_pattern=events.EventPattern(
                    source=['aws.ec2'],
                    detail_type=['AWS API Call via CloudTrail'],
                    detail={
                        "eventSource": [
                            "ec2.amazonaws.com"
                        ],
                        "eventName": [
                            event_name
                        ]
                    }
                )
            )
            ec2_rule.add_target(targets.SnsTopic(alert_topic))

        cloudtrail_event_names = [
            "StopLogging",
            "DeleteTrail",
            "UpdateTrail"
        ]

        for event_name in cloudtrail_event_names:
            cloudtrail_rule = events.Rule(
                self, 'CloudTrail{}Rule'.format(event_name),
                event_pattern=events.EventPattern(
                    source=['aws.cloudtrail'],
                    detail_type=['AWS API Call via CloudTrail'],
                    detail={
                        "eventSource": [
                            "cloudtrail.amazonaws.com"
                        ],
                        "eventName": [
                            event_name
                        ]
                    }
                )
            )
            cloudtrail_rule.add_target(targets.SnsTopic(alert_topic))

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
