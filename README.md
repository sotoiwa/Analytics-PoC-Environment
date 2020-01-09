# CDKサンプルプロジェクト

## 前提

ローカルPCから実行する場合Node.jsとpythonの実行環境が必要です。Cloud9環境からの実行もおすすめです。
AdministratorAccessを持つユーザーでの実行を想定しています。必要なクレデンシャルをローカルPCに配置するか、Cloud9環境のIAMロールに与えて下さい。

- [cloud9.md](cloud9.md)

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
|account|AWSアカウント。|
|region|リージョン。|
|key_name|Proxyインスタンスに配置するキーペアの名前。|

### デプロイ

VPCをデプロイします。

```
cdk deploy *VpcStack *VpcPeeringStack --require-approval never
```

監査ログ設定をデプロイします。

```
cdk deploy *AuditLogStack --require-approval never
```

暗号化用のキーとIAMユーザーをデプロイします。

```
cdk deploy *IamStack --require-approval never
```

データ保管用のバケットをデプロイします。

```
cdk deploy *BucketStack --require-approval never
```

Proxyサーバーをデプロイします。

```
cdk deploy *ProxyStack --require-approval never
```

## WorkSpaces

WorkSpacesについてはCDKではなくマネージメントコンソールからの払い出しを行います。

- [workspaces.md](workspaces.md)

## SAP

SAP環境についてはクイックスタートを使ってマネージメントコンソールから構築します。