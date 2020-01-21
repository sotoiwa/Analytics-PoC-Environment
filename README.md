# CDKサンプルプロジェクト

## 前提

- AWSアカウントが作成済みとします。
- デプロイは管理者権限を持つIAMユーザーの権限で行うため、IAMユーザーを用意して下さい。
- あらかじめ、環境をデプロイするリージョンにキーペアを用意して下さい。このキーペアはProxyインスタンスに設定します。
- EIPを4つ使用するため、既にVPCを作成済みの環境ではアカウントのEIP数の上限（デフォルトでは5）に引っかかる可能性があります。必要に応じてEIP数の上限緩和申請をして下さい。
- ローカルPC（Mac）からCDKでのデプロイを実行する場合、Node.jsとPythonの実行環境が必要です。
  - 他にも、この手順の全ての操作を実行するためには、awscli、jq、git、cfsslも必要です。

```
brew install python
brew install node
brew install awscli
brew install jq
brew install git
brew install cfssl
```

- Windowsの場合は環境のコマンドラインツールのセットアップが難しいため、Cloud9環境からの実行がおすすめです。下記の手順を参考にしてCloud9環境をセットアップして下さい。
  - [Cloud9環境のセットアップ](cloud9.md)

## 環境デプロイ手順

### CDKのインストール

CDKをグローバルにインストールします。

```
npm install -g aws-cdk
```

### CDKプロジェクトのクローン

CDKプロジェクトをローカルにクローンします。

```
git clone https://github.com/sotoiwa/aws-cdksample.git
cd aws-cdksample
```

### Pythonの準備

Pythonのvirtualenvを作成して有効化します。

```
python3 -m venv .env
source .env/bin/activate
```

必要なモジュールをインストールします。

```
pip install -r requirements.txt
```

### 環境に合わせたカスタマイズ

`cdk.context.json.sample`を`cdk.context.json`としてコピーします。
以下パラメータを自分の環境に合わせてカスタマイズします。

|パラメータ|デフォルト値|備考|
|---|---|---|
|account|（設定必須）|環境をデプロイするAWSアカウントを指定します。|
|region|`ap-northeast-1`|環境をデプロイするリージョンを指定します。|
|key_name|（設定必須）|事前に作成したキーペアの名前を指定します。このキーペアはProxyインスタンスに配置されます。|
|hosted_zone|`corp.example.com`|Workspacesドメインのドメインを指定します。|
|nat_gateway_eips|`0.0.0.0/0`|NATゲートウェイが作成されてから指定するため、デフォルトのままにします。|
|admin_user_names|`admin-user`|管理者ユーザーの名前のリスト。|
|environment_admin_user_names|`environment-admin-user`|環境管理者ユーザーの名前のリストを指定します。|
|security_audit_user_names|`security-audit-user`|セキュリティ監査者ユーザーの名前のリストを指定します。|
|data_scientist_user_names|`data-scientist-user`|分析者ユーザーの名前のリストを指定します。|
|redshift.master_user_password|（設定必須）|RedShiftのマスターユーザーのパスワードを指定します。下記のパスワード要件があるため注意して下さい。|

（補足）RedShiftのマスターユーザーのパスワード要件

- 値は 8 ～ 64 文字長である必要があります。
- 値には、少なくとも 1 つの大文字が含まれている必要があります。
- 値には、少なくとも 1 つの小文字が含まれている必要があります。
- 値には、少なくとも 1 つの数字が含まれている必要があります。
- マスターパスワードには、印刷可能な ASCII 文字 (ASCII コード 33-126) のみを含めることができます。ただし、`'`(一重引用符) 、`”`(二重引用符)、`/`、`@`、またはスペースは除きます。

### デプロイ

キーとバケットをデプロイします。

```
cdk deploy *BucketStack --require-approval never
```

VPCをデプロイします。

```
cdk deploy *VpcStack *VpcPeeringStack --require-approval never
```

WorkSpaces用のVPCのNAT GatewayにアタッチされているEIPのアドレスを、マネージメントコンソールまたはAWS CLIで確認します。

```
aws ec2 describe-nat-gateways | jq '.NatGateways[] | select( [ .Tags[] | select( .Value | test("WorkSpaces") ) ] | length > 0 ) | .NatGatewayAddresses[].PublicIp'
```

このアドレスを`cdk.context.json`に記載します。1つめのアドレスと2つめのアドレスの間にはカンマが必要です。

```
  "nat_gateway_eips": [
    "18.176.193.136", 
    "3.115.222.230"
  ],
```

監査ログ設定をデプロイします。

```
cdk deploy *AuditLogStack --require-approval never
```

IAMユーザーをデプロイします。

```
cdk deploy *IamStack --require-approval never
```

Proxyサーバーと踏み台サーバーをデプロイします。

```
cdk deploy *ProxyStack *BastionStack --require-approval never
```

RedShiftクラスターをデプロイします。

```
cdk deploy *RedShiftStack --require-approval never
```

SageMakerノートブックインスタンスをデプロイします。

```
cdk deploy *SageMakerStack --require-approval never
```

## WorkSpaces

WorkSpacesについてはCDKではなくマネージメントコンソールからの払い出しを行います。

- [WorkSpacesのセットアップ](workspaces.md)

## SAP

SAP環境についてはクイックスタートを使ってマネージメントコンソールから構築します。

- [AWS クラウドでの SAP HANA: クイックスタートリファレンスデプロイ](https://docs.aws.amazon.com/ja_jp/quickstart/latest/sap-hana/welcome.html)

## パスワード

### IAMユーザーのパスワードポリシー

以下のポリシーを設定します。

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

### IAMユーザーのパスワードの取得

IAMユーザーのパスワードはCDKデプロイ時に生成され、Secret Managerに格納されています。
管理者はSecret Managerでパスワードを取得し、ユーザーに連携します。ユーザーは初回ログイン時にパスワードを変更する必要があります。

### RedShiftのパスワードの変更

RedShiftのパスワードは`cdk.context.json`で指定しました。
このパスワードはCloudFormationのテンプレートにも出力されており、テキストとして閲覧可能は状態にあるため、マネージメントコンソールからパスワードを変更して下さい。
