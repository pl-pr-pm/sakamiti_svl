"""
Dailyで、対象日付の対象のディレクトリを削除する。
EventBridgeをトリガーとする。
対象基底ディレクトリ,削除対象マイナス日はSSM パラメータに保持。
"""
import logging
import datetime

# loggerの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# SSMパラメータから削除基底ディレクトリを取得
base_remove_directory = os.environ['target_housekeep']
logger.debug(f'base_remove_directory is {base_remove_directory}')

# SSMパラメータから削除対象マイナス日を取得
remove_diff_day = os.environ['remove_diff_day']
logger.debug(f'remove_diff_day is {remove_diff_day}')

def lambda_handler(event, context):
    
    try:
      if not remove_diff_day.isdigit():
          logger.error(f'remove_diff_dayが数値でない。remove_diff_dayを数値で入力する必要がある。: {remove_diff_day}')
          
      # 削除ディレクトリパスに利用
      target_date = datetime.datetime.now() - datetime.timedelta(days=remove_diff_day)
      target_date_str = target_date.strftime('%Y%m%d')
      
      # 削除ディレクトリ構築
      target_remove_dir = base_remove_directory+target_date_str+'/'
      logger.debug(f'target_remove_dir = {target_remove_dir}')
      
      # ディレクトリ削除
      shutil.rmtree(target_remove_dir)
      logger.debug(f'ディレクトリ削除完了: {target_remove_dir}')
      
      
    except Exception as e:
        logger.debug(e)
        logger.error(f'ディレクトリ削除失敗: {target_remove_dir}')
