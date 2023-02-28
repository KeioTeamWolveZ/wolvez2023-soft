import cv2
import numpy as np
import os
from PIL import Image
from matplotlib import pyplot as plt
from time import time

class ReadFeaturedImg():
    """画像読込関数
    
    Args:
        importPath (str): Original img path
        saveDir (str): Save directory path that allowed tmp
        Save(bool):Save or not, defalt:False
    """
    def __init__(self, importPath:str=None, saveDir:str=None, Save:any=False):
        self.imp_p = importPath
        self.sav_d = saveDir
        self.save = Save
    
    def feature_img(self, frame_num, feature_names=None):
        '''Change to treated img
        Args:
            frame_num(int):Frame number or time
            feature_name(str):
        '''
        self.treat = Feature_img(self.imp_p, frame_num, self.sav_d)
        if feature_names == None:
            self.treat.normalRGB()
            #self.treat.vari()
            #self.treat.rgbvi()
            #self.treat.grvi()
            #self.treat.ior()
            self.treat.enphasis()
            self.treat.edge()
            self.treat.hsv()
            self.treat.r()
            self.treat.b()
            self.treat.g()
            self.treat.rb()
            self.treat.gb()
            self.treat.rg()
            
        else:
            for feature_name in feature_names:
                if feature_name == "normalRGB":
                    self.treat.normalRGB()
                #elif feature_name == "vari":
                    #self.treat.vari()
                #elif feature_name == "rgbvi":
                    #self.treat.rgbvi()
                #elif feature_name == "grvi":
                    #self.treat.grvi()
                #elif feature_name == "ior":
                    #self.treat.ior()
                elif feature_name == "enphasis":
                    self.treat.enphasis()
                elif feature_name == "edge":
                    self.treat.edge()
                elif feature_name == "hsv":
                    self.treat.hsv()
                elif feature_name == "red":
                    self.treat.r()
                elif feature_name == "blue":
                    self.treat.b()
                elif feature_name == "green":
                    self.treat.g()
                elif feature_name == "purple":
                    self.treat.rb()
                elif feature_name == "emerald":
                    self.treat.gb()
                elif feature_name == "yellow":
                    self.treat.rg()
                else:
                    self.treat.other()
        fmg_list = self.treat.output()
        
        return fmg_list


    def read_img(self, path):
        #print("===== func read_img starts =====")
        self.img=cv2.imread(path,cv2.IMREAD_GRAYSCALE)
        self.img = self.img[int(0.25*self.img.shape[0]):int(0.75*self.img.shape[0])]
        # 読み込めないエラーが生じた際のロバスト性も検討したい
        return self.img



class Feature_img():
    save_name = None
    def __init__(self, imp_p, frame_num, saveDir):
        self.output_img_list = []
        self.imp_p = imp_p
        self.frame_num = frame_num
        self.sav_d = saveDir

    
    def normalRGB(self):
        self.org_img = np.array(Image.open(self.imp_p))
        self.save_name = self.sav_d + f"/normalRGB_{self.frame_num}.jpg"
        self.output_img = Image.fromarray(self.org_img)
        self.output_img.save(self.save_name)
        #cv2.imwrite(self.save_name, self.output_img)
        self.output_img_list.append(self.save_name)

    # 赤色抽出
    def r(self):
        #self.output_img_list = []
        self.org_img = np.array(Image.open(self.imp_p))
        self.org_img[:, :, 1] = np.zeros((self.org_img.shape[0],self.org_img.shape[1]))
        self.org_img[:, :, 2] = np.zeros((self.org_img.shape[0],self.org_img.shape[1]))
        self.save_name = self.sav_d + f"/red_{self.frame_num}.jpg"
        self.output_img = Image.fromarray(self.org_img)
        self.output_img.save(self.save_name)
        #cv2.imwrite(self.save_name, self.output_img)
        self.output_img_list.append(self.save_name)

    # 青色抽出
    def b(self):
        #self.output_img_list = []
        self.org_img = np.array(Image.open(self.imp_p))
        self.org_img[:, :, 0] = 0
        self.org_img[:, :, 1] = 0
        self.save_name = self.sav_d + f"/blue_{self.frame_num}.jpg"
        self.output_img = Image.fromarray(self.org_img)
        self.output_img.save(self.save_name)
        #cv2.imwrite(self.save_name, self.output_img)
        self.output_img_list.append(self.save_name)

    # 緑色抽出
    def g(self):
        #self.output_img_list = []
        self.org_img = np.array(Image.open(self.imp_p))
        self.org_img[:, :, 0] = 0
        self.org_img[:, :, 2] = 0
        self.save_name = self.sav_d + f"/green_{self.frame_num}.jpg"
        self.output_img = Image.fromarray(self.org_img)
        self.output_img.save(self.save_name)
        #cv2.imwrite(self.save_name, self.output_img)
        self.output_img_list.append(self.save_name)

    # 緑色排除
    def rb(self):
        #self.output_img_list = []
        self.org_img = np.array(Image.open(self.imp_p))
        self.org_img[:, :, 1] = 0
        self.save_name = self.sav_d + f"/purple_{self.frame_num}.jpg"
        self.output_img = Image.fromarray(self.org_img)
        self.output_img.save(self.save_name)
        #cv2.imwrite(self.save_name, self.output_img)
        self.output_img_list.append(self.save_name)

    # 赤色排除
    def gb(self):
        #self.output_img_list = []
        self.org_img = np.array(Image.open(self.imp_p))
        self.org_img[:, :, 0] = 0
        self.save_name = self.sav_d + f"/emerald_{self.frame_num}.jpg"
        self.output_img = Image.fromarray(self.org_img)
        self.output_img.save(self.save_name)
        #cv2.imwrite(self.save_name, self.output_img)
        self.output_img_list.append(self.save_name)
    
    # 青色排除
    def rg(self):
        #self.output_img_list = []
        self.org_img = np.array(Image.open(self.imp_p))
        self.org_img[:, :, 2] = 0
        self.save_name = self.sav_d + f"/yellow_{self.frame_num}.jpg"
        self.output_img = Image.fromarray(self.org_img)
        self.output_img.save(self.save_name)
        #cv2.imwrite(self.save_name, self.output_img)
        self.output_img_list.append(self.save_name)

    # VARI
    def vari(self):
        #self.output_img_list = []
        self.org_img = cv2.imread(self.imp_p,1)
        self.vari_list_np = np.ones((self.org_img.shape[0],self.org_img.shape[1]), np.float64)
        self.output_img = np.ones((self.org_img.shape[0],self.org_img.shape[1]), np.uint8)
        for i in range(self.org_img.shape[0]):
            for j in range(self.org_img.shape[1]):
                vari = 0.0
                b = float(self.org_img[i][j][0])
                g = float(self.org_img[i][j][1])
                r = float(self.org_img[i][j][2])
                if b < 125:
                    vari_d = g+r-b
                    if vari_d != 0:
                        vari = (g-r)/(g+r-b)
                        if vari < 0.0:
                            vari = 0.0
                else:
                    vari = 0
                # vari = vari*255/9.0
                self.vari_list_np[i][j] = vari

        vari_max = np.amax(self.vari_list_np)
        vari_min = np.amin(self.vari_list_np)
        #print("vari max: "+str(np.amax(self.vari_list_np)))
        #print("vari min: "+str(np.amin(self.vari_list_np)))
        for i in range(self.org_img.shape[0]):
            for j in range(self.org_img.shape[1]):
                self.vari_list_np[i][j] = 100*(self.vari_list_np[i][j] - vari_min)/(vari_max - vari_min)
                if self.vari_list_np[i][j] > 1.0:
                    self.vari_list_np[i][j] = 1.0
                self.vari_list_np[i][j] = 255*self.vari_list_np[i][j]
                # print(self.vari_list_np[i][j])
                # print(np.uint8(self.vari_list_np[i][j]))
                self.output_img[i][j] = np.uint8(self.vari_list_np[i][j])
        #print("len(self.vari_list_np): "+str(self.vari_list_np.shape))
        #print("vari max: "+str(np.amax(self.vari_list_np)))
        #print("vari min: "+str(np.amin(self.vari_list_np)))
        #print(self.vari_list_np)

        #cv2.imshow("self.org_img", cv2.resize(self.org_img,dsize=(534,400)))
        #cv2.imshow("VARI_img",cv2.resize(self.output_img,dsize=(534,460)))

        self.save_name = self.sav_d + f"/vari_{self.frame_num}.jpg"
        cv2.imwrite(self.save_name, self.output_img)
        self.output_img_list.append(self.save_name)
        
    # RGBVI
    def rgbvi(self):
        self.org_img = cv2.imread(self.imp_p,1)
        self.rgbvi_list_np = np.ones((self.org_img.shape[0],self.org_img.shape[1]), np.float64)
        self.output_img = np.ones((self.org_img.shape[0],self.org_img.shape[1]), np.uint8)
        for i in range(self.org_img.shape[0]):
            for j in range(self.org_img.shape[1]):
                rgbvi = 0.0
                b = float(self.org_img[i][j][0])
                g = float(self.org_img[i][j][1])
                r = float(self.org_img[i][j][2])
                if g*g+r*b != 0:
                    rgbvi = (g*g-r*b)/(g*g+r*b)     # ここがGRVIの計算式
                else:
                    rgbvi = (g*g-r*b)/0.01 
                self.vari_list_np[i][j] = rgbvi
                self.output_img[i][j] = np.uint8(self.rgbvi_list_np[i][j])
        self.save_name = self.sav_d + f"/rgbvi_{self.frame_num}.jpg"
        cv2.imwrite(self.save_name, self.output_img)
        self.output_img_list.append(self.save_name)

    # GRVI（緑赤植生指標）
    def grvi(self):
        self.org_img = cv2.imread(self.imp_p,1)
        self.grvi_list_np = np.ones((self.org_img.shape[0],self.org_img.shape[1]), np.float64)
        self.output_img = np.ones((self.org_img.shape[0],self.org_img.shape[1]), np.uint8)
        for i in range(self.org_img.shape[0]):
            for j in range(self.org_img.shape[1]):
                grvi = 0.0
                b = float(self.org_img[i][j][0])
                g = float(self.org_img[i][j][1])
                r = float(self.org_img[i][j][2])
                grvi = (g-r)/(g+r)     # ここがGRVIの計算式
                self.grvi_list_np[i][j] = grvi
                self.output_img[i][j] = np.uint8(self.grvi_list_np[i][j])
        self.save_name = self.sav_d + f"/grvi_{self.frame_num}.jpg"
        cv2.imwrite(self.save_name, self.output_img) 
        self.output_img_list.append(self.save_name)

    # IOR（酸化鉄比）ARLISSで使用できるかも？
    def ior(self):
        self.org_img = cv2.imread(self.imp_p,1)
        self.ior_list_np = np.ones((self.org_img.shape[0],self.org_img.shape[1]), np.float64)
        self.output_img = np.ones((self.org_img.shape[0],self.org_img.shape[1]), np.uint8)
        for i in range(self.org_img.shape[0]):
            for j in range(self.org_img.shape[1]):
                ior = 0.0
                b = float(self.org_img[i][j][0])
                g = float(self.org_img[i][j][1])
                r = float(self.org_img[i][j][2])
                ior = r/b     # ここがGRVIの計算式
                self.ior_list_np[i][j] = ior
                self.output_img[i][j] = np.uint8(self.ior_list_np[i][j])
        self.save_name = self.sav_d + f"/ior_{self.frame_num}.jpg"
        cv2.imwrite(self.save_name, self.output_img) 
        self.output_img_list.append(self.save_name)
    
    # エッジ強調
    def enphasis(self):
        #self.output_img_list = []
        self.org_img = cv2.imread(self.imp_p, 1)
        self.org_img = cv2.cvtColor(self.org_img, cv2.COLOR_BGR2RGB)
        kernel = np.array([[0, 2, 0],
                            [2, -8, 2],
                            [0, 2, 0]], np.float32)
        self.output_img = cv2.filter2D(self.org_img, -1, kernel)
        self.save_name = self.sav_d + f"/enphasis_{self.frame_num}.jpg"
        cv2.imwrite(self.save_name, self.output_img)
        self.output_img_list.append(self.save_name)
    
    # エッジ検出
    def edge(self):
        #self.output_img_list = []
        self.org_img = cv2.imread(self.imp_p, 1)
        self.img_gray = cv2.cvtColor(self.org_img, cv2.COLOR_BGR2GRAY)
        self.gray=cv2.Canny(self.img_gray,100,200)
        self.save_name = self.sav_d + f"/edge_{self.frame_num}.jpg"
        cv2.imwrite(self.save_name,self.gray)
        self.output_img_list.append(self.save_name)
        
    def hsv(self):
        #self.output_img_list = []
        self.org_img = cv2.imread(self.imp_p, 1)
        self.img_hsv = cv2.cvtColor(self.org_img, cv2.COLOR_BGR2HSV)
        self.save_name = self.sav_d + f"/hsv_{self.frame_num}.jpg"
        cv2.imwrite(self.save_name,self.img_hsv)
        self.output_img_list.append(self.save_name)
    
    def other(self):
        self.save_name = "0"
        self.output_img_list.append(self.save_name)
        
    # 特徴抽出済画像パス引き渡し
    def output(self):
        return self.output_img_list
    
    # 作ってみたが使わない
    def show(self):
        k = 0
        for img in self.output_img_list:
            plt.subplot(int(f"1{len(self.output_img_list)}{k}"))
            plt.imshow(img)
            ax = plt.gca()
            ax.axes.xaxis.set_visible(False)
            ax.axes.yaxis.set_visible(False)
            plt.title(f"img_{self.frame_num}")
            k += 1
        plt.show()




# if __name__ == "__main__":
#     feat = Feature_img(["img_data/data_old/img_train_RPC.jpg"])
#     train_img_path = feat.vari()