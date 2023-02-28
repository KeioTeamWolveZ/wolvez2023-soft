import re
import os
import cv2
import numpy as np
from datetime import datetime
from glob import glob
from math import prod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from baba_into_window import IntoWindow
from bbaa_learn_dict import LearnDict
from bcaa_eval import EvaluateImg

import time

class Bspm():
    def __init__(self, saveDir=None):
        # 一旦一枚目だけ学習
        self.saveDir = saveDir

        if not os.path.exists(self.saveDir):
            os.mkdir(self.saveDir)
        if not os.path.exists(self.saveDir + f"/bbba_learnimg"):
            os.mkdir(self.saveDir + f"/bbba_learnimg")
        if not os.path.exists(self.saveDir + f"/bcca_secondinput"):
            os.mkdir(self.saveDir + f"/bcca_secondinput")
        saveName = self.saveDir + f"/bcba_difference"
        if not os.path.exists(saveName):
            os.mkdir(saveName)
        
    
    def mainExecutor(self, learn_state, feature_name, now, dict_list, importPath=None):
        
        self.now=now
        saveName = self.saveDir + f"/bcba_difference/{now}"
        if not os.path.exists(saveName):
            os.mkdir(saveName)
        Save = True
        
        # Path that img will be read
        #importPath = path.replace("\\", "/")
        
        # This will change such as datetime
        print("CURRENT FRAME: "+str(re.findall(".*/frame_(.*).jpg", importPath)[0]))
        
        iw_shape = (2, 3)
        D, ksvd = None, None
        feature_values = {}

        if learn_state:
            print("=====LEARNING PHASE=====")
            self.dict_list = {}
        else:
            print("=====EVALUATING PHASE=====")
            self.dict_list = dict_list

        
        
        
        iw = IntoWindow(importPath, self.saveDir, Save)
        # processing img
        fmg_list = iw.feature_img(frame_num=now, feature_name=feature_name)
        
        fmg = fmg_list[0]
        # breakout by windows
        iw_list, window_size = iw.breakout(iw.read_img(fmg))
        feature_name = str(re.findall(self.saveDir + f"/baca_featuring/(.*)_.*_", fmg)[0])
        print("FEATURED BY: ",feature_name)
        for win in range(int(prod(iw_shape))):
            #print("PRAT: ",win+1)
            if learn_state:
                if win+1 == int((iw_shape[0]-1)*iw_shape[1]) + int(iw_shape[1]/2) + 1:
                    ld = LearnDict(iw_list[win])
                    D, ksvd = ld.generate()
                    self.dict_list[feature_name] = [D, ksvd]
                    save_name = self.saveDir + f"/bbba_learnimg/{feature_name}_part_{win+1}_{now}.jpg"
                    cv2.imwrite(save_name, iw_list[win])
            else:
                D, ksvd = self.dict_list[feature_name]
                ei = EvaluateImg(iw_list[win])
                img_rec = ei.reconstruct(D, ksvd, window_size)
                saveName = self.saveDir + f"/bcba_difference/{now}"
                if not os.path.exists(saveName):
                    os.mkdir(saveName)
                ave, med, var = ei.evaluate(iw_list[win], img_rec, win+1, feature_name, now, self.saveDir)
                #if win+1 == int((iw_shape[0]-1)*iw_shape[1]) + int(iw_shape[1]/2) + 1:
                #    feature_values[feature_name] = {}
                #    feature_values[feature_name]["var"] = ave
                #    feature_values[feature_name]["med"] = med
                #    feature_values[feature_name]["ave"] = var
                
                if not feature_name in feature_values:
                    feature_values[feature_name] = {}
                feature_values[feature_name][f'win_{win+1}'] = {}
                feature_values[feature_name][f'win_{win+1}']["var"] = ave
                feature_values[feature_name][f'win_{win+1}']["med"] = med
                feature_values[feature_name][f'win_{win+1}']["ave"] = var
        
        
        
        # Learn state should be changed by main.py
        #learn_state = False

        return feature_values, self.dict_list