# Cloud9環境のセットアップ

cdkをCloud9から実行する場合の環境の払い出し手順を以下に記載します。

## IAMロールの準備

以下の手順で、Cloud9が使用するインスタンスロールを作成します。

1. マネジメントコンソールで、**サービス**から**IAM**を選択します。
1. 左のメニューから**ロール**を選択します。
1. **ロールの作成**をクリックし、**AWSサービス**と**EC2**を選択して**次のステップ**へ進みます。
1. **AdministratorAccess**にチェックをして**次のステップ**へ進みます。
1. タグはそのままにして**次のステップ**へ進みます。
1. ロールに`MyCloud9InstanceRole`のような適当な名前をつけて、**ロールの作成**を行います。

## 環境の払い出し

以下の手順で、Cloud9環境をデプロイします。

1. マネジメントコンソールで、**サービス**から、**開発者用ツール**カテゴリにある **Cloud9**を選択します。
1. **リージョン**が**東京**であることを確認します。
1. **Create environment**ボタンをクリックします。
1. **Name environment**画面で、**Name**に`MyCloud9`など適当な名前を入力します。
1. 画面右下の**Next step**ボタンをクリックします。
1. **Configure settings**画面では、**Enviroment type**で、**EC2**が選択されていることを確認します。
1. **Instance type**では好みのタイプを選択し、画面右下の**Next step**ボタンをクリックします。
1. **Review**画面で、画面右下の**Create environment**ボタンをクリックします。

## インスタンスロールの設定

Cloud9は呼び出したAWSアカウントが利用可能な全てのAWSリソースに対するAWSアクションを許可する一時的なクレデンシャルで利用できますが、一部に制限があるため、明示的にインスタンスロールを割り当てます。

以下の手順で、Cloud9のインスタンスにロールを割り当てます。

1. マネジメントコンソールで**サービス**から**EC2**を選択します。
1. 左のメニューから**インスタンス**を選択します。
1. Cloud9のインスタンスをチェックします。
1. **アクション**から**インスタンスの設定**の**IAMロールの割り当て/置換**を選択し、先ほど作成したIAMロールを選択し、**適用**します。

以下の手順で、一時的なクレデンシャルの利用を無効にします。

1. Cloud9で右上の設定アイコンを選択します。
1. **AWS SETTINGS**の**AWS managed temporary credentials**を無効にします。

## バージョン確認

Node.js、Python等のバージョンを確認します。

```
node -v
npm -v
python --version
aws --version
```

## AWS CLIの初期設定

画面下部のターミナルから、下記のコマンドを実行し、AWS CLIに東京リージョンを指定します。

```
$ aws configure
AWS Access Key ID [None]: <空ENTER>
AWS Secret Access Key [None]: <空ENTER>
Default region name [None]: ap-notheast-1
Default output format [None]: <空ENTER>
```

## 追加ソフトウェアのインストール

セットアップで使用するいくつかのソフトウェアを追加で導入します。

```
# jq
sudo yum -y install jq
# cfssl
curl -Lo cfssl https://github.com/cloudflare/cfssl/releases/download/v1.4.1/cfssl_1.4.1_linux_amd64
curl -Lo cfssljson https://github.com/cloudflare/cfssl/releases/download/v1.4.1/cfssljson_1.4.1_linux_amd64
chmod +x cfssl cfssljson
sudo mv cfssl cfssljson /usr/local/bin/
cfssl version
```
