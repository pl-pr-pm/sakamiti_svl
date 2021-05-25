import os
import sys
import logging

class ResizeImage():
    def __init__(self, sakamiti:str, mode:str, resize_shape=(139, 139)):
        """
        init
        
        Args:
           sakamiti (str): グループ名、出力パス等に利用
           resize_shape (tuple): 学習するネットワークのサイズ 
                                      デフォルトはファインチューニングする入力のサイズとしている
           mode (str): リサイズのモード (顔抽出前リサイズ or 顔抽出後リサイズ)
           
        Returns:
            None
        """
        self._resize_shape = resize_shape
        self._sakamiti = sakamiti
        
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # EFSからモジュールのインポートを行う
        sys.path.insert(0,'/mnt/efs/lib')
        logger.info(sys.path)

        from PIL import Image
        
        if mode == "pre":
            self.resize_dir = "./pic/" +  self._sakamiti + "/pre_resize/"
        else:
            self.resize_dir = "./pic/" +  self._sakamiti + "/resize/"

    def resize_image(self, input_image_path:str, output_image_path:str = None):
        """ 
        入力された画像をopen cvを使って学習するネットワークのサイズにリサイズする
        
        Args:
           input_image_path (str): リサイズ対象の画像
           output_image_path (str): リサイズ後の画像出力先
                                            デフォルト None
        
        Returns:
           None
        """
        logger.info(f'input_image_path = {input_image_path}')
        
        # メソッドの引数に output_image_path( ) が指定されなかった場合、出力先のパス変数を生成する
        if output_image_path is None:
            
           # ファイル名直上ディレクトリ名（＝メンバー名）を取得
           member_name = input_image_path.split('/')[-2:-1] 
        
           # ファイル名を取得
           resize_path = self.resize_dir + member_name[0] 
        
        resize_path = output_image_path
        
           #入力画像ファイルの親ディレクトリが存在しない場合、ディレクトリを作成する
        if not os.path.exists(resize_path):
            os.makedirs(resize_path)
            
            logger.info(f'出力ディレクトリが存在しなかったため {resize_path} を作成しました。')
            
        img = Image.open(input_image_path)
        
        # 対象のネットワークの入力サイズに画像をリサイズする
        resize_img = img.resize(size=self._resize_shape)
        
        resize_output_path = os.path.join(resize_path, os.path.basename(input_image_path))
        
        # リサイズし、RGBに変換した画像を保存する
        resize_img.save(resize_output_path, quality=95)
        
        logger.info(f'リサイズ画像を {resize_output_path} として保存しました。')
