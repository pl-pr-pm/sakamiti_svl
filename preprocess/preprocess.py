"""

リクエストのあった画像を prediction で利用できるように加工する。
1. リクエスト画像のリサイズ
2. リサイズした画像から face_recognition を利用して顔のみ抽出
3. prediction にて利用するモデルが許容するサイズに再度リサイズ

########################
Request Http(s) Example:
########################

curl -d \
body : {
   'input_file_path': /hoge/piyo/... <- 顔が載っている画像パス
   }
https://~ models/preprocess

########################
Response Http(s) Example:
########################


IN CASE OF 200

headers = {
    'Content-Type': 'application/json'
}

body = {
   'output_file_path':/hoge/piyo/...  <- 加工済み画像のパス
}


IN CASE OF 500

headers = {
    'Content-Type': 'application/json'
}

body = {
   'error_message': 'Something Error Happened' <- エラーメッセージ
}

"""


import json
import logging
import datetime
import uuid
import os
import sys

# loggerの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# インポートモジュールが大きすぎて、layersを利用できないため、
# EFS上にインポートモジュールを配置
# pythonのインポートサーチディレクトリにEFS上のモジュールが格納されているパスを追加
sys.path.insert(0,'/mnt/efs/lib')

from sakamiti.resize_image import ResizeImage
from sakamiti.extract_face import ExtractFace

# レスポンスヘッダに利用
KEY_CONTENT_TYPE = 'Content-Type'
VAL_CONTENT_TYPE = 'application/json'
KEY_ORIGIN = 'Access-Control-Allow-Origin'
VAL_ORIGIN = '*'

# レスポンスに利用
OK_STATUS_CODE = 200
SERVER_ERROR_STATUS_CODE = 500

# コールドスタート時にインスタンス化し、処理の効率化を図る
preresizer = ResizeImage(sakamiti="user", resize_shape=(516, 516), mode="pre")
extracter = ExtractFace(sakamiti="user")
resizer = ResizeImage(sakamiti="user", mode="main")

def lambda_handler(event, context):
    
    try:
       logger.info(f'event = {event}')
       #logger.info(event['body'])
       #input_file_path = json.dumps(event['body']['input_file_path'])
       # 元々は、リクエストのjsonのキーを 'input_file_path' としていたが、
       # なぜか、リクエストのjsonが文字列として認識される(""で括られる)ため、lambda側でjsonのパースができなかった
       # そのため、bodyのキーに直接対象の値を入れている
       
       input_file_path = event['body']
       logger.info(input_file_path)
       
       path = os.path.split(input_file_path)
       
       base_output_file_path = path[0]
       filename = path[1]
       
       # メモリに乗せられる大きさの画像にリサイズ
       output_file_path =  base_output_file_path + '/preresize/'
    
       preresizer.resize_image(input_image_path=input_file_path, output_image_path=output_file_path)
    
       # １度リサイズした画像から顔抽出
       output_face_image_path=base_output_file_path + '/extract/'
       extracter.extract_face(original_face_image_path=output_file_path + filename, output_face_image_path=output_face_image_path)
       
       # ネットワークの入力サイズにリサイズ
       output_file_path =  base_output_file_path + 'resize/'
       resizer.resize_image(input_image_path=output_face_image_path + filename, output_image_path=output_file_path)
       
       body = {
           'output_file_path':output_file_path + filename
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
        
        logger.error("type : %s" , type(e))
        logger.error(e)
        
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
    
    return response