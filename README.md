# CDKサンプルプロジェクト

## 前提

ローカルPCから実行する場合Node.jsとPython等の実行環境が必要です。

```
brew install python
brew install node
brew install awscli
brew install jq
brew install git
```

Windowsの場合は環境のセットアップが面倒と思われるため、Cloud9環境からの実行がおすすめです。

- [Cloud9環境のセットアップ](cloud9.md)

## 環境構築手順

### CDKのインストール

```
npm install -g aws-cdk
```

### CDKプロジェクトのクローン

```
git clone https://github.com/sotoiwa/aws-cdksample.git
```

### Pythonの準備

virtualenvを作成して有効化します。

```
cd aws-cdksample
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

|パラメータ|説明|
|---|---|
|account|AWSアカウント|
|region|リージョン|
|key_name|Proxyインスタンスに配置するキーペアの名前。|
|admin_user_names|管理者ユーザーの名前のリスト|
|environment_admin_user_names|環境管理者ユーザーの名前のリスト|
|security_audit_user_names|セキュリティ監査者ユーザーの名前のリスト|
|data_scientist_user_names|分析者ユーザーの名前のリスト|
|redshift.master_user_password|edShiftのマスターユーザーのパスワード|

（補足）RedShiftのマスターユーザーのパスワード要件

- 値は 8 ～ 64 文字長である必要があります。
- 値には、少なくとも 1 つの大文字が含まれている必要があります。
- 値には、少なくとも 1 つの小文字が含まれている必要があります。
- 値には、少なくとも 1 つの数字が含まれている必要があります。
- マスターパスワードには、印刷可能な ASCII 文字 (ASCII コード 33-126) のみを含めることができます。ただし、'(一重引用符) 、” (二重引用符)、/、@、またはスペースは除きます。

### デプロイ

VPCをデプロイします。

```
cdk deploy *VpcStack *VpcPeeringStack --require-approval never
```

WorkSpaces用のVPCのNAT GatewayにアタッチされているEIPのアドレスを、マネージメントコンソールまたはAWS CLIで確認します。

```
aws ec2 describe-nat-gateways | jq '.NatGateways[] | select( [ .Tags[] | select( .Value | test("WorkSpaces") ) ] | length > 0 ) | .NatGatewayAddresses[].PublicIp'
```

このアドレスを`cdk.context.json`に記載します。

```
  "nat_gateway_eips": [
    "18.176.193.136", 
    "3.115.222.230"
  ],
```

IAMユーザーをデプロイします。

```
cdk deploy *IamStack --require-approval never
```

監査ログ設定をデプロイします。

```
cdk deploy *AuditLogStack --require-approval never
```

データ保管用のバケットをデプロイします。

```
cdk deploy *BucketStack --require-approval never
```

Proxyサーバーと踏み台サーバーをデプロイします。

```
cdk deploy *ProxyStack *BasionStack --require-approval never
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

## パスワードポリシーの設定

以下のポリシーを設定する。

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
