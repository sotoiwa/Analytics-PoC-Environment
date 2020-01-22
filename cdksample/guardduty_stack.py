from aws_cdk import (
    core,
    aws_events as events,
    aws_events_targets as targets,
    aws_guardduty as guardduty,
)


class GuardDutyStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        alert_topic = props['alert_topic']

        ################
        # GuardDutyの有効化の設定
        ################

        if not self.node.try_get_context('guardduty_already_enabled'):
            guardduty.CfnDetector(
                self, 'Detector',
                enable=True,
                finding_publishing_frequency='SIX_HOURS'
            )

        # GuardDuty
        guardduty_rule = events.Rule(
            self, 'GuardDutyRule',
            event_pattern=events.EventPattern(
                source=['aws.guardduty'],
                detail_type=['GuardDuty Finding']
            )
        )
        guardduty_rule.add_target(targets.SnsTopic(alert_topic))

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
