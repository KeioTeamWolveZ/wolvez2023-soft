import os
import numpy as np
import pandas as pd
from bbaa_learn_dict import LearnDict
from sklearn.preprocessing import StandardScaler
from spmimage.feature_extraction.image import reconstruct_from_simple_patches_2d
import matplotlib.pyplot as plt


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
        return np.average(diff),np.median(diff),np.var(diff),diff_df.kurt().to_numpy()[0],diff_df.skew().to_numpy()[0]