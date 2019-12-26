import string
import secrets

from aws_cdk import (
    core,
    aws_iam as iam
)


class IamStack(core.Stack):

    # @staticmethod
    # def generate_password(size=12):
    #     """パスワード生成関数
    #     :return:
    #     """
    #     chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    #     # 記号を含める場合
    #     # chars += '%&$#()'
    #     return ''.join(secrets.choice(chars) for x in range(size))

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # IAM
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_iam.html

        # 職務機能の AWS 管理ポリシー
        # https://docs.aws.amazon.com/ja_jp/IAM/latest/UserGuide/access_policies_job-functions.html

        ################
        # ロールの作成
        ################

        # 管理者ロールの作成
        admin_role = iam.Role(
            self, 'AdministratorAccessRole',
            role_name='AdministratorAccessRole',
            assumed_by=iam.AccountPrincipal(self.node.try_get_context('account'))
        )
        admin_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AdministratorAccess'))

        # Billingロールの作成
        billing_role = iam.Role(
            self, 'BillingRole',
            role_name='BillingRole',
            assumed_by=iam.AccountPrincipal(self.node.try_get_context('account'))
        )
        billing_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('job-function/Billing'))

        # パワーユーザーロールの作成
        power_user_role = iam.Role(
            self, 'PowerUserAccessRole',
            role_name='PowerUserAccessRole',
            assumed_by=iam.AccountPrincipal(self.node.try_get_context('account'))
        )
        power_user_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('PowerUserAccess'))

        ################
        # グループの作成
        ################

        # 管理者グループ
        # 管理者ロール、Billingロール、パワーユーザロールへのスイッチロールのみを許可する
        admin_group = iam.Group(
            self, 'AdminGroup',
            group_name='AdminGroup'
        )
        # スイッチロールを許可するインラインポリシー
        admin_switch_policy = iam.Policy(
            self, 'AdminSwitchPolicy',
            policy_name='AdminSwitchPolicy',
            statements=[
                iam.PolicyStatement(
                    actions=['sts:AssumeRole'],
                    resources=[
                        admin_role.role_arn,
                        billing_role.role_arn,
                        power_user_role.role_arn
                    ]
                )
            ]
        )
        admin_switch_policy.attach_to_group(admin_group)

        # 分析者グループ
        # グループにポリシーを直接アタッチする
        data_scientist_group = iam.Group(
            self, 'DataScientistGroup',
            group_name='DataScientistGroup'
        )
        data_scientist_group.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name('job-function/DataScientist'))

        # セキュリティ監査グループ
        # グループにポリシーを直接アタッチする
        security_audit_group = iam.Group(
            self, 'SecurityAuditGroup',
            group_name='SecurityAuditGroup'
        )
        security_audit_group.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('SecurityAudit'))

        ################
        # IPアドレス制限
        ################

        # IPアドレス制限を行う管理ポリシー
        ip_address_policy = iam.ManagedPolicy(
            self, 'IpAddressPolicy',
            managed_policy_name='IpAddressPolicy',
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.DENY,
                    actions=['*'],
                    resources=['*'],
                    conditions={
                        'NotIpAddress': {
                            'aws:SourceIp': '72.21.198.66/32'
                        }
                    }
                )
            ]
        )

        # ポリシーをグループにアタッチ
        ip_address_policy.attach_to_group(admin_group)
        ip_address_policy.attach_to_group(data_scientist_group)
        ip_address_policy.attach_to_group(security_audit_group)

        ################
        # グループの作成
        ################

        # 管理者ユーザーの作成
        admin_user_names = ['admin-user']
        for user_name in admin_user_names:
            password = self.node.try_get_context('default_password')
            user = iam.User(
                self, user_name,
                user_name=user_name,
                password=core.SecretValue.plain_text(password),
                password_reset_required=False
            )
            user.add_to_group(admin_group)
            core.CfnOutput(
                self, '{}Password'.format(user_name),
                description='Password for user {}'.format(user_name),
                value=password
            )

        # 分析者ユーザーの作成
        data_scientist_user_names = ['data-user']
        for user_name in data_scientist_user_names:
            password = self.node.try_get_context('default_password')
            user = iam.User(
                self, user_name,
                user_name=user_name,
                password=core.SecretValue.plain_text(password),
                password_reset_required=True
            )
            user.add_to_group(data_scientist_group)
            core.CfnOutput(
                self, '{}Password'.format(user_name),
                description='Password for user {}'.format(user_name),
                value=password
            )

        # セキュリティ監査ユーザーの作成
        security_audit_user_names = ['audit-user']
        for user_name in security_audit_user_names:
            password = self.node.try_get_context('default_password')
            user = iam.User(
                self, user_name,
                user_name=user_name,
                password=core.SecretValue.plain_text(password),
                password_reset_required=True
            )
            user.add_to_group(security_audit_group)
            core.CfnOutput(
                self, '{}Password'.format(user_name),
                description='Password for user {}'.format(user_name),
                value=password
            )

        self.output_props = props.copy()

    @property
    def outputs(self):
        return self.output_props
