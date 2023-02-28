from baaa_feature import ReadFeaturedImg
import os
import pandas as pd
import numpy as np
from spmimage.feature_extraction.image import extract_simple_patches_2d
from sklearn.preprocessing import StandardScaler
from spmimage.decomposition import KSVD
from bbaa_learn_dict import LearnDict
from spmimage.feature_extraction.image import reconstruct_from_simple_patches_2d
import matplotlib.pyplot as plt

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
    

class LearnDict():
    patch_size=(40,71)
    n_components=5
    transform_n_nonzero_coefs=4
    max_iter=15
    def __init__(self, img_part:np.ndarray):
        self.train_img = img_part
        self.Y = self.img_to_Y(self.train_img, self.patch_size)
    
    def generate(self):
        self.D, self.ksvd = self.__generate_dict(Y=self.Y, n_components=self.n_components,
                                                 transform_n_nonzero_coefs=self.transform_n_nonzero_coefs, max_iter=self.max_iter)
        return self.D, self.ksvd
    
    def img_to_Y(self, train_img, patch_size=(40,71)):
        self.scl=StandardScaler()
        #print("===== func img_to_Y starts =====")
        self.patches=extract_simple_patches_2d(train_img,patch_size=patch_size)# 画像をpatch_sizeに分割
        self.patches=self.patches.reshape(-1, np.prod(patch_size))# 2次元に直す。(枚数,patchの積) つまりパッチを2→1次元にしている
        #print("patch_size: ",patches.shape)# (枚数,patch_size[0],patch_size[1])つまり３じげん
        self.Y=self.scl.fit_transform(self.patches)# 各パッチの標準化（スケールの違いを標準化する）
        #print("patches were standardized")
        return self.Y
    
    def __generate_dict(self, Y=None, n_components=20, transform_n_nonzero_coefs=3, max_iter=15):
        """
        入力 : 学習画像データ群Y
        出力 : 辞書D・スパースコード（=抽出行列α）X・学習したモデルksvd
        機能 : 画像データ群Yを構成する基底ベクトルの集合Dを生成
            Yを再構成するためにどうDの中身を組み合わせるか、を示すXも生成
            この際、基底ベクトルの数をn_componentsで指定できる
            また、各画素の再構成に使える基底ベクトルの本数をtransform_n_nonzero_coefsで指定できる
            max_iterは詳細不明
        """
        #print("===== func generate_dict starts =====")
        # 学習モデルの定義
        self.ksvd = KSVD(n_components=n_components,
                    transform_n_nonzero_coefs=transform_n_nonzero_coefs, max_iter=max_iter)
        #print("model established. Parameters are:")
        #print("n_components: ", n_components)
        #print("transform_n_nonzero_coefs: ", transform_n_nonzero_coefs)
        #print("max_iter: ", max_iter)
        # 抽出行列を求める
        self.X = self.ksvd.fit_transform(Y)
        #print("X shape: ", self.X.shape)
        # 辞書を求める
        self.D = self.ksvd.components_
        #print("D shape: ", self.D.shape)

        return self.D, self.ksvd
    



class EvaluateImg(LearnDict):
    def __init__(self, eval_img:np.ndarray):
        self.Y = super().img_to_Y(eval_img)
    
        self.patch_size = super().patch_size
    
    def reconstruct(self,D,ksvd, original_img_size):
        #print("===== func reconstruct_img starts =====")
        X=ksvd.transform(self.Y)
        Y_rec=np.dot(X,D)
        #print("Y was reconstructed by D")
        scl=StandardScaler()
        scl.fit(Y_rec) # おまじない
        # 0-255の画素値に戻す
        if (Y_rec.max()-Y_rec.min()) == 0:
            Y_rec=scl.inverse_transform(Y_rec)*255/0.1+255/2
        else:
            Y_rec=scl.inverse_transform(Y_rec)*255/(Y_rec.max()-Y_rec.min())+255/2
        # 配列の整形
        Y_rec=Y_rec.reshape(-1,self.patch_size[0],self.patch_size[1])
        # 画像の復元
        img_rec=reconstruct_from_simple_patches_2d(Y_rec,original_img_size)
        
        # エラーの修正
        img_rec[img_rec<0]=0
        img_rec[img_rec>255]=255
        # 型の指定
        img_rec=img_rec.astype(np.uint8)    
        return img_rec
    
    def evaluate(self,img,img_rec,d_num, feature_name, time, saveDir):
        """
        学習画像・正常画像・異常画像それぞれについて、
        ・元画像
        ・再構成画像
        ・画素値の偏差のヒストグラム
        を出力
        """
        #ax1 = plt.subplot2grid((2,2), (0,0))
        #ax2 = plt.subplot2grid((2,2), (0,1))
        #ax3 = plt.subplot2grid((2,2), (1,0))
        #ax4 = plt.subplot2grid((2,2), (1,1))
        #ax1.imshow(img, cmap='gray')
        #ax1.set_title("original img")
        #ax2.imshow(img_rec, cmap='gray')
        #ax2.set_title("reconstructed img")
        diff=abs(img-img_rec)
        diff_df = pd.DataFrame(diff.reshape(-1,))
        val, count = np.unique(diff, return_counts=True)
        index = np.argmax(count)
        mode = val[index]
        #ax3.imshow(diff*255,cmap='gray')
        #ax3.set_title("difference")
        #ax4.hist(diff.reshape(-1,),bins=255,range=(0,255))
        #ax4.set_title("histgram")
        #save_title=str(datetime.datetime.now()).replace(" ","_").replace(":","-")
        #plt.savefig(os.getcwd()+"/img_result/"+save_title+".png")
        #self.saveName = saveDir + f"/bcba_difference/{time}"
        #plt.savefig(self.saveName+f"/{feature_name}_part_{d_num}.jpg")
        #print("average: ",np.average(diff))
        #print("median: ",np.median(diff))
        #print("variance: ",np.var(diff))
        return np.average(diff),np.median(diff),np.var(diff),mode,diff_df.kurt().to_numpy()[0],diff_df.skew().to_numpy()[0]