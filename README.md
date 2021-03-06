# Analytics-PoC-Environment

#### インフラ構成

![](images/architecture.png)

#### CDKスタックの依存関係

![](images/stack-dependencies.png)

## 前提

- AWSアカウントが作成済みとします。
- デプロイは管理者権限を持つIAMユーザーの権限で行うため、IAMユーザーを用意して下さい。
- あらかじめ、環境をデプロイするリージョンにキーペアを用意して下さい。このキーペアはProxyインスタンスに設定します。
- EIPを2つ使用するため、既にVPCを作成済みの環境ではアカウントのEIP数の上限（デフォルトでは5）に注意し、必要に応じてEIP数の上限緩和申請をして下さい。
- CDKを実行環境のセットアップを容易にするため、Cloud9環境を使用します。

## Cloud9環境のセットアップ

以下の手順に従ってCloud9をセットアップして下さい。

- [Cloud9環境のセットアップ](cloud9.md)

## アカウントの基本的な設定

アカウントレベルでの基本的な設定をCDKではなくCLIで行います。

IAMユーザーのパスワードポリシーを設定します。このポリシーは以下のようなポリシーです。

- パスワードの最小文字数は 8 文字です
- 1 文字以上のアルファベット大文字 (A～Z) を必要とする
- 1 文字以上のアルファベット小文字 (a～z) を必要とする
- Require at least one number
- Require at least one non-alphanumeric character (!@#$%^&*()_+-=[]{}|')
- パスワードは 30 日で有効期限が切れます
- Allow users to change their own password
- 直近 10 回分のパスワードを記憶して再利用を防ぐ

```
aws iam update-account-password-policy \
  --minimum-password-length 8 \
  --require-symbols \
  --require-numbers \
  --require-uppercase-characters \
  --require-lowercase-characters \
  --allow-users-to-change-password \
  --max-password-age 30 \
  --password-reuse-prevention 10
```

アカウントレベルでS3のブロックパブリックアクセスを有効にします。

```
ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)
aws s3control put-public-access-block \
  --account-id ${ACCOUNT_ID} \
  --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true
```

GuardDutyを有効化します。

```
aws guardduty create-detector --enable
```

## 環境デプロイ手順

### CDKのインストール

CDKをグローバルにインストールします。

```
npm install -g aws-cdk
```

### CDKプロジェクトのクローン

CDKプロジェクトをローカルにクローンします。

```
git clone https://github.com/sotoiwa/Analytics-PoC-Environment.git
cd Analytics-PoC-Environment
```

### Pythonの準備

Pythonのvirtualenvを作成して有効化します。

```
python3 -m venv .env
source .env/bin/activate
```

必要なpipモジュールをインストールします。

```
pip install -r requirements.txt
```

### 環境に合わせたカスタマイズ

`cdk.context.sample.json`を`cdk.context.json`としてコピーします。

```
cp cdk.context.sample.json cdk.context.json
```


以下パラメータを自分の環境に合わせて適宜カスタマイズします。特に以下のパラメータは必須です。

|パラメータ|デフォルト値|備考|
|---|---|---|
|`stack_prefix`|`PoC`|デプロイするCloudFormationスタック名のプレフィックス。|
|`bucket_suffix`|`poc`|作成するS3バケットのサフィックス。|
|`account`|（設定必須）|環境をデプロイするAWSアカウントを指定して下さい。アカウントIDの確認コマンドは下記（補足1）を参照。|
|`region`|`ap-northeast-1`|環境をデプロイするリージョンを指定して下さい。|
|`default_user_password`|（設定必須）|IAMユーザーのデフォルトのパスワードを指定します。パスワード要件を上で設定しているため注意して下さい。|
|`admin_user_names`|`admin-user`|管理者ユーザーの名前のリスト。yamadaのようなユーザー名のリストを指定して下さい。|
|`environment_admin_user_names`|`environment-admin-user`|環境管理者ユーザーの名前のリストを指定して下さい。|
|`security_audit_user_names`|`security-audit-user`|セキュリティ監査者ユーザーの名前のリストを指定して下さい。|
|`data_scientist_user_names`|`data-scientist-user`|分析者ユーザーの名前のリストを指定して下さい。|
|`redshift.master_user_password`|（設定必須）|Redshiftのマスターユーザーのパスワードを指定して下さい。下記（補足2）のパスワード要件があるため注意して下さい。|
|`proxy.key_name`|（設定必須）|事前に作成したキーペアの名前を指定して下さい。このキーペアはProxyインスタンスに配置されます。|
|`allow_ips`|`0.0.0.0/0`|マネージメントコンソールへのアクセスを許可するIPアドレスのリストを指定しますが、ここではデフォルトのまま（無制限）にして下さい。|
|`emales_to_alert`|（設定必須）|アラートメールの宛先のEメールアドレスのリストを指定して下さい。|

（補足1）アカウントIDの確認コマンド

```
aws sts get-caller-identity --output text --query Account
```

（補足2）Redshiftのマスターユーザーのパスワード要件

- 値は 8 ～ 64 文字長である必要があります。
- 値には、少なくとも 1 つの大文字が含まれている必要があります。
- 値には、少なくとも 1 つの小文字が含まれている必要があります。
- 値には、少なくとも 1 つの数字が含まれている必要があります。
- マスターパスワードには、印刷可能な ASCII 文字 (ASCII コード 33-126) のみを含めることができます。ただし、`'`(一重引用符) 、`”`(二重引用符)、`/`、`@`、またはスペースは除きます。

### デプロイ

CDKが使用するバケットを作成します。

```
cdk bootstrap
```

VPCとセキュリティグループをデプロイします。
なお、この際、WorkSpaces用のVPCのCloudWatchのVPCエンドポイントを、デプロイ対象から除外しています。
これはSimple ADの作成時にCloudWatchのVPCエンドポイントが存在するとエラーとなるという既知の事象の回避のためです。

```
cdk deploy *NetworkStack --require-approval never
```

IAM設定をデプロイします。

```
cdk deploy *IamStack --require-approval never
```

キーとバケットをデプロイします。

```
cdk deploy *BucketStack --require-approval never
```

監査ログ設定をデプロイします。

```
cdk deploy *AuditLogStack --require-approval never
```

Events、Config設定をデプロイします。

```
cdk deploy *EventsStack *ConfigStack --require-approval never
```

Proxyサーバーと踏み台サーバーをデプロイします。

```
cdk deploy *ProxyStack *BastionStack --require-approval never
```

Redshiftクラスターをデプロイします。

```
cdk deploy *RedshiftStack --require-approval never
```

SageMakerノートブックインスタンスをデプロイします。

```
cdk deploy *SageMakerStack --require-approval never
```

IPアドレス制限を有効化します。WorkSpaces用のVPCのNAT GatewayにアタッチされているEIPのアドレスを、マネージメントコンソールまたはAWS CLIで確認します。

```
aws ec2 describe-nat-gateways | jq '.NatGateways[] | select( [ .Tags[] | select( .Value | test("WorkSpaces") ) ] | length > 0 ) | .NatGatewayAddresses[].PublicIp'
```

このアドレスを`cdk.context.json`に記載します。1つめのアドレスと2つめのアドレスの間にはカンマが必要です。

```
  "allow_ips": [
    "18.176.193.136", 
    "3.115.222.230"
  ],
```

IPアドレス制限のIAM設定を更新します。

```
cdk deploy *IamStack --require-approval never
```

Redshiftクラスターの拡張VPCルーティングをCLIから有効にします。クラスター識別子は`cdk.context.json`の`redshift.cluster_identifier`で指定したものです。

```
cluster_identifier=$(cat cdk.context.json | jq -r '.redshift.cluster_identifier')
aws redshift modify-cluster \
  --cluster-identifier ${cluster_identifier} \
  --enhanced-vpc-routing
```

## 踏み台サーバーの削除

稼働確認後、踏み台サーバーは削除します。

```
cdk destroy -f *BastionStack
```

### IAMユーザーのパスワードの取得

IAMユーザーのパスワードは`cdk.context.json`で指定しました。
このパスワードはCloudFormationのテンプレートにも出力されており、テキストとして閲覧可能は状態にあります。ユーザーは初回ログイン時にパスワードを変更する必要があります。

### Redshiftのパスワードの変更

Redshiftのパスワードは`cdk.context.json`で指定しました。
このパスワードはCloudFormationのテンプレートにも出力されており、テキストとして閲覧可能は状態にあるため、マネージメントコンソールからパスワードを変更して下さい。

## WorkSpaces

WorkSpacesについてはCDKではなくマネージメントコンソールからの払い出しを行います。

- [WorkSpacesの払い出し](workspaces-deploy.md)
- [WorkSpacesの利用](workspaces-use.md)

### VPCエンドポイントの作成

VPCのデプロイ時、WorkSpaces用のVPCには意図的にCloudWatchのエンドポイントを作成していませんでした。
これはSimple ADの作成時にCloudWatchのVPCエンドポイントが存在するとエラーとなるという既知の事象の回避のためです。
Simple ADの作成が終わったあと、VPCエンドポイントを作成します。

`network_stack.py`で以下の部分をアンコメントします。

```
        # WorkSpaces用にVPCのCloudWatchのVPCエンドポイントを作成
        # このエンドポイントが存在するとSimple ADの作成に失敗するのでコメントアウト
        workspaces_vpc_cloudwatch_endpoint = workspaces_vpc.add_interface_endpoint(
            id='WorkSpacesVPCCloudWatchEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH,
            private_dns_enabled=True,
            security_groups=[workspaces_vpc_endpoint_sg],
            subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED)
        )
```

スタックを更新します。

```
cdk deploy *NetworkStack --require-approval never
```

### WorkSpacesのログイン記録

WorkSpacesへのログインを記録するCloudWatch Events Ruleを作成します。CDKからRuleのターゲットとしてCloudWatch Logsを指定できないため、GUIで作成します。

![](images/events-rule01.png)

![](images/events-rule02.png)

## SAP

SAP環境についてはクイックスタートを使ってマネージメントコンソールから構築します。

- [AWS クラウドでの SAP HANA: クイックスタートリファレンスデプロイ](https://docs.aws.amazon.com/ja_jp/quickstart/latest/sap-hana/welcome.html)

## 環境の削除

CDKからデプロイしたリソースは`cdk destroy`コマンドで削除できますが、CDKからデプロイしたリソースに依存するCDKの管理外のリソースがあると削除に失敗します。
先にそれらのリソースを手動で削除して下さい。例えば、以下のリソースです。

- Proxyインスタンスが起動時に登録するRoute 53のレコードセット（proxy.example.com）
- WorkSpacesインスタンス、Simple AD

CDKからデプロイしたリソースの削除は以下のコマンドで実施します。

```
cdk destroy -f *Stack
```
