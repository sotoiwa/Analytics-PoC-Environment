from aws_cdk import (
    core,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions
)


class GlobalEventsStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # コンソールログインとIAM関係のイベントはus-east-1に作成する必要がある

        # メール通知用のトピック
        alert_topic = sns.Topic(
            self, 'AlertTopic'
        )
        # サービスにトピックへのPublish権限を付与
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
        alert_topic.add_subscription(subscriptions.EmailSubscription('sotoiwa@gmail.com'))

        # rootユーザーのログインの監視
        root_login_rule = events.Rule(
            self, 'RootLoginRule',
            event_pattern=events.EventPattern(
                detail_type=['AWS Console Sign In via CloudTrail'],
                detail={
                    "userIdentity": {
                        "type": [
                            "Root"
                        ]
                    }
                }
            )
        )
        root_login_rule.add_target(targets.SnsTopic(alert_topic))

        # コンソールログインを監視するユーザーのリスト
        login_usernames = [
            "sotosugi",
        ]

        # 監視ルールを定義
        for username in login_usernames:
            login_rule = events.Rule(
                self, '{}LoginRule'.format(username),
                event_pattern=events.EventPattern(
                    detail_type=['AWS Console Sign In via CloudTrail'],
                    detail={
                        "userIdentity": {
                            "type": [
                                "IAMUser"
                            ],
                            "userName": [
                                username
                            ]
                        }
                    }
                )
            )
            login_rule.add_target(targets.SnsTopic(alert_topic))

        # IAMの監視対象イベント
        iam_event_names = [
            "DeleteRole",
            "DeleteGroupPolicy",
            "DeleteRolePolicy",
            "DeleteUserPolicy",
            "DetachGroupPolicy",
            "DetachRolePolicy",
            "DetachUserPolicy",
            "PutGroupPolicy",
            "PutRolePolicy",
            "PutUserPolicy"
        ]

        # 監視ルールを定義
        for event_name in iam_event_names:
            iam_rule = events.Rule(
                self, 'Iam{}Rule'.format(event_name),
                event_pattern=events.EventPattern(
                    source=['aws.iam'],
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
            iam_rule.add_target(targets.SnsTopic(alert_topic))

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
