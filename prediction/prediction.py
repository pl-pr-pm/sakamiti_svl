"""

リクエストのあった画像から事前学習済みのモデルを利用して坂道グループ （乃木坂/ 日向坂/ 櫻坂）における類似度の計算を行う。
API gateway のバックエンドとして起動
preprocess 実行後に本APIを呼び出す

########################
Request Http(s) Example:
########################

curl -d \
body : {
   'output_file_path': /hoge/piyo/... <- 事前学習済みモデルのネットワークに適したarray sizeにリサイズ済みの画像パス
   }
https://~ models/prediction

########################
Response Http(s) Example:
########################


IN CASE OF 200

headers = {
    'Content-Type': 'application/json'
}

body = {
   'predicted_group':nogizaka  <- 最も類似度の高いグループ名
   'predicted_list':[0.334, 0.566, 0.1]   <- 類似度のリスト [乃木坂, 日向坂, 櫻坂]
}


IN CASE OF 500

headers = {
    'Content-Type': 'application/json'
}

body = {
   'error_message': 'Something Error Happened' <- エラーメッセージ
}

"""

import os
import sys
import json
import logging

# レスポンスヘッダに利用
KEY_CONTENT_TYPE = 'Content-Type'
VAL_CONTENT_TYPE = 'application/json'

# レスポンスに利用
OK_STATUS_CODE = 200
SERVER_ERROR_STATUS_CODE = 500
CREATED_STATUS_CODE = 201
KEY_ORIGIN = 'Access-Control-Allow-Origin'
VAL_ORIGIN = '*'

# loggerの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# インポートモジュールが大きすぎて、layersを利用できないため、
# EFS上にインポートモジュールを配置
# pythonのインポートサーチディレクトリにEFS上のモジュールが格納されているパスを追加

sys.path.insert(0,'/mnt/efs/lib')

# EFSからモジュールをインポート
import numpy as np
from keras import models
from PIL import Image

# 学習済みのモデルを読み込む
new_model = models.load_model('/mnt/efs/model/fine-tuning-sakamiti.h5')
logger.debug('モデル読み込み完了')

def lambda_handler(event, context):
    
    try:
       
       logger.debug(f'event = {event}')
       if 'body' not in event:
           
           response = {
           'statusCode':CREATED_STATUS_CODE,
           'body':'',
           'headers':{
               KEY_CONTENT_TYPE:VAL_CONTENT_TYPE,
               KEY_ORIGIN: VAL_ORIGIN
                }
           }
           logger.debug('warm up が完了')
           return response
           
       output_file_path = event['body']
       logger.debug(f'output_file_path is {output_file_path}')
    
       # リクエストのあった画像を読み込み、配列の要素データを0 ~ 1にスケールする
       image = Image.open(output_file_path)
       nparray = np.array(image)
       nparray = nparray.astype('float32')
       nparray /= 255
    
       # モデルに読み込むことが可能な形にreshapeする -> (1, 139, 139, 3)
       reshaped_nparray = nparray.reshape(1,nparray.shape[0], nparray.shape[1], nparray.shape[2])
       
       # 事前学習済みモデルを利用して画像のグループへの類似度を計算する
       # model.predict()は、小さい入力では遅いとのことで、model(x)を利用し、処理の高速化を図る
       # https://github.com/tensorflow/tensorflow/blob/v2.4.1/tensorflow/python/keras/engine/training.py#L1502-L1647
       
       predicted_list = new_model(reshaped_nparray)
    
       logger.debug(f'predicted_list is {predicted_list}')
    
       # 最も確度の高い要素のインデックスを取得する
       predicted = np.argmax(predicted_list)
    
       group = ""
       
       # インデックスからグループ名を割り当て
       if predicted == 0: group = "nogizaka"
       if predicted == 1: group = "hinatazaka"
       if predicted == 2: group = "sakurazaka"
       
    
       body = {
           'predicted_group':group,
           'predicted_list':str(predicted),
       }
       
       response = {
           'statusCode':OK_STATUS_CODE,
           'body':json.dumps(body),
           'headers':{
               KEY_CONTENT_TYPE:VAL_CONTENT_TYPE,
               KEY_ORIGIN: VAL_ORIGIN
           },
       }
    except Exception as e:
        
        logging.error("type : %s" , type(e))
        logging.error(e)
        
        body = {
            'error_message': e.args
        }
        
        response = {
            'statusCode':SERVER_ERROR_STATUS_CODE,
            'body':json.dumps(body),
            'headers':{
               KEY_CONTENT_TYPE:VAL_CONTENT_TYPE,
               KEY_ORIGIN: VAL_ORIGIN
           },
        }
    
    logger.debug(f'response is {response}')
    return response
