# クライアント証明書の作成

[cfssl](https://github.com/cloudflare/cfssl)を使って、オレオレ認証局と、オレオレ認証局が署名したクライアント証明書を作成します。

## cfsslのインストール

cfsslをまだインストールしていない場合はインストールします。

```
# Macの場合
brew install cfssl
# Linuxの場合
wget https://github.com/cloudflare/cfssl/releases/download/v1.4.1/cfssl_1.4.1_linux_amd64
wget https://github.com/cloudflare/cfssl/releases/download/v1.4.1/cfssljson_1.4.1_linux_amd64
chmod +x cfssl cfssljson
sudo mv cfssl cfssljson /usr/local/bin/
# バージョン確認
cfssl version
# 次のステップに備えてディレクトリを移動
cd certificates
```

## CA

ルートCAの設定ファイルのjsonを作成します。
workspacesというプロファイルを定義し、このCAが署名する証明書の有効期限と、X509v3拡張で証明書に含まれるパブリックキーの用途を指定します。
後でCAから証明書を発行するときにこの設定ファイルとプロファイルを指定します。

```
cd certificates
cat > ca-config.json <<EOF
{
  "signing": {
    "default": {
      "expiry": "8760h"
    },
    "profiles": {
      "workspaces": {
        "usages": ["signing", "key encipherment", "server auth", "client auth"],
        "expiry": "8760h"
      }
    }
  }
}
EOF
```

ルートCAのCSR（証明書署名要求）を作成するためのjsonを作成します。

```
cat > ca-csr.json <<EOF
{
  "CN": "corp.example.com",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "JP",
      "O": "Example Company"
    }
  ]
}
EOF
```

CA秘密鍵（`ca-key.pem`）とCA証明書（`ca.pem`）を作成します。
このとき証明書署名要求（`ca.csr`）も作成されます。
前半の`cfssl gencert`コマンドが秘密鍵とCSRと証明書を作成し、出力されたjsonを`cfssljson`コマンドがファイルにしています。

```
cfssl gencert -initca ca-csr.json | cfssljson -bare ca
```

鍵、CSR、証明書の内容を確認します。

```
# 鍵
openssl rsa -text -noout -in ca-key.pem
# CSR
openssl req -text -noout -in ca.csr
# 証明書
openssl x509 -text -noout -in ca.pem
```

## クライアント証明書の作成

設定ファイルを作成します。

```
cat > hogehoge-csr.json <<EOF
{
  "CN": "hogehoge",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "JP",
      "O": "Example Company"
    }
  ]
}
EOF
```

秘密鍵と証明書を作成します。

```
cfssl gencert \
  -ca=ca.pem \
  -ca-key=ca-key.pem \
  -config=ca-config.json \
  -profile=workspaces \
  hogehoge-csr.json | cfssljson -bare hogehoge
```

秘密鍵、クライアント証明書、CA証明書をp12形式にまとめます。パスフレーズが聞かれるので設定します。

```
openssl pkcs12 -export -inkey hogehoge-key.pem -in hogehoge.pem -certfile ca.pem -out hogehoge.p12
```
