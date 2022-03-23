# sakamiti_svl

画像グループ診断 Web アプリケーションのバックエンド・インフラリポジトリ
画像を受け付け、その画像の人物の特徴からグループを推論する

### 機能

1. API gateway + lambda にてリクエストをリッスン
2. リクエストされた画像を EFS にアップロードし、加工、そして推論
3. 推論した結果をレスポンスする

#### エンドポイント

1. upload(画像アップロード)
2. preprocess(アップロード画像の加工)
3. prediction(画像推論)

### インフラ定義

AWS sam を利用し IaaC を実現（一部オリジナルで作成済みのリソースを参照している）

- VPC
- EFS
- API Gateway
- Lambda
  - upload(画像アップロード)
  - preprocess(アップロード画像の加工)
  - prediction(画像推論)
