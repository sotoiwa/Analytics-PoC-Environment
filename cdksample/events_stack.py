from aws_cdk import (
    core,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
)


class EventsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # メール通知用のトピック
        alert_topic = sns.Topic(
            self, 'AlertTopic'
        )
        # トピックポリシーを設定
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
        # サブスクリプションを設定
        emails = self.node.try_get_context('emails_to_alert')
        for email in emails:
            alert_topic.add_subscription(subscriptions.EmailSubscription('sotoiwa@gmail.com'))

        # EC2の監視対象イベントのリスト
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

        # 監視ルールを定義
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

        # CloudTrailの監視対象イベントのリスト
        cloudtrail_event_names = [
            "StopLogging",
            "DeleteTrail",
            "UpdateTrail"
        ]

        # 監視ルールを定義
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
