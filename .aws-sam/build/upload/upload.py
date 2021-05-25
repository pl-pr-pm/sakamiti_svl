"""
クライアントからの画像アップロードリクエストを引き受け、EFS上に画像を保存する
保存した画像をlambda間で利用する

########################
Request Http(s) Example:
########################

axios.post(url, targetFile, {
                headers: {
                    "Content-Type": targetFile.type
                }
            }

########################
Response Http(s) Example:
########################


IN CASE OF 200

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*'
}

body = {
   'saved_file_path':/mnt/efs/pic/${now_str}/${uuid_str}/target.${extention}  <- アップロード画像の保存パス
}


IN CASE OF 500

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*'
}

body = {
   'error_message': 'Something Error Happened' <- エラーメッセージ
}

"""


import json
import base64
import io
import sys
import logging
import uuid
import datetime
import os

# loggerの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# EFS上にインポートモジュールを配置
# pythonのインポートサーチディレクトリにEFS上のモジュールが格納されているパスを追加
sys.path.insert(0,'/mnt/efs/lib')

from PIL import Image

# レスポンスヘッダに利用
KEY_CONTENT_TYPE = 'Content-Type'
VAL_CONTENT_TYPE = 'application/json'
KEY_ORIGIN = 'Access-Control-Allow-Origin'
VAL_ORIGIN = '*'

# レスポンスに利用
OK_STATUS_CODE = 200
SERVER_ERROR_STATUS_CODE = 500

def lambda_handler(event, context):
       
    try:
           
      logger.info(f'event = {event}')
      # Content-Typeを取得
      # 保存ファイルパスに利用
      c_type = event['headers']['content-type']
      extention = c_type.split('/')[1]
      logger.info(f'extention = {extention}')
    
      # 保存ファイルパスに利用
      now = datetime.datetime.now()
      now_str = now.strftime('%Y%m%d')
    
      # 保存ファイルパスに利用
      uuid_str = str(uuid.uuid4())
    
      # 保存ファイルディレクトリ
      base_output_path = "/mnt/efs/pic/" + now_str + '/' + uuid_str
      logger.info(f'base_output_path = {base_output_path}')
      
      # 保存ファイルディレクトリを作成
      os.makedirs(base_output_path)
      logger.info(f'directory created {base_output_path}')
      
      # 保存ファイルパス
      base_output_file_path = "/mnt/efs/pic/" + now_str + '/' + uuid_str + '/' + 'target.' + extention
      
      # 画像データを取得
      content = event['body']
 
      # エンコードした画像データをバイナリに変換
      b_content = base64.b64decode(content)
    
      # バイナリから画像に変換
      """
      Image.open時、Image.Image.loadが呼ばれ、その後ファイルオブジェクトがcloseされるため、明示的にcloseはしない
      https://qiita.com/shizuma/items/968ea45ad411d0e702e6
      """
    
      target_image = Image.open(io.BytesIO(b_content))
      target_image.save(base_output_file_path)
      logger.info(f'image saved at {base_output_file_path}')

      response =  {
          'statusCode': OK_STATUS_CODE,
          'headers': {
              KEY_CONTENT_TYPE:VAL_CONTENT_TYPE,
              KEY_ORIGIN: VAL_ORIGIN
          },
          "body": json.dumps({
              "saved_file_path": base_output_file_path,
              }),
      }
      
    except Exception as e:
        
      logger.error("type : %s" , type(e))
      logger.error(e)        
        
      response =  {
          "statusCode": SERVER_ERROR_STATUS_CODE,
          "headers": {
              KEY_CONTENT_TYPE:VAL_CONTENT_TYPE,
              KEY_ORIGIN: VAL_ORIGIN
          },
          "body": json.dumps({
              'error_message': e.args,
          }),
      } 
    return response
