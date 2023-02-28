from baaa_feature import ReadFeaturedImg
import numpy as np

class IntoWindow(ReadFeaturedImg):
    def __init__(self, importPath:str=None, saveDir:str=None, Save:bool=False):
        super().__init__(importPath, saveDir, Save)

    def breakout(self, img:np.ndarray=None, windowshape:tuple=(2,3)):
        """画像探査領域分割関数

        Args:
            img (np.ndarray): 画像
            windowshape (list, optional): 所望の領域のシェイプ. Defaults to (2, 3).

        Returns:
            list: 3 lists of separated img.
        """
        self.img_window_list = []
        height = img.shape[0]
        width = img.shape[1]
        
        # 指定の大きさの探査領域を設定
        partial_height = int(height/windowshape[0])
        partial_width = int(width/windowshape[1])
        # 探査領域を抽出
        for i in range(windowshape[0]):
            for j in range(windowshape[1]):
                img_part = img[i*partial_height:(i+1)*partial_height, j*partial_width:(j+1)*partial_width]
                
                # まとめて返すためのリストに追加
                self.img_window_list.append(img_part)
        
        return self.img_window_list, (partial_height, partial_width)