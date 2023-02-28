import time
import shutil
import os
from datetime import datetime
import glob

class Cansat():
    def __init__(self):
        #初期パラメータ設定
        self.startTime = str(datetime.now())[:19].replace(" ","_").replace(":","-")
        self.learncount = 1
        self.mkdir()
        self.mkfile()
        self.mvfile()

    def mkdir(self): #フォルダ作成部分
        folder_paths =[f"test/{self.startTime}",
                       f"test/{self.startTime}/camera_result",
                       f"test/{self.startTime}/camera_result/first_spm",
                       f"test/{self.startTime}/camera_result/first_spm/learn{self.learncount}",
                       f"test/{self.startTime}/camera_result/first_spm/learn{self.learncount}/evaluate",
                       f"test/{self.startTime}/camera_result/first_spm/learn{self.learncount}/processed",
                       f"test/{self.startTime}/camera_result/second_spm",
                       f"test/{self.startTime}/camera_result/second_spm/learn{self.learncount}",
                       f"test/{self.startTime}/camera_result/planning",
                       f"test/{self.startTime}/camera_result/planning/learn{self.learncount}",
                       f"test/{self.startTime}/camera_result/planning/learn{self.learncount}/planning_npz",
                       f"test/{self.startTime}/camera_result/planning/learn{self.learncount}/planning_pics"]
        
        for folder_path in folder_paths:
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

    def mkfile(self):
        control_path = open(f'test/{self.startTime}/control_result.txt', 'w')
        control_path.close()
        planning_path = open(f'test/{self.startTime}/planning_result.txt', 'w')
        planning_path.close()

    def mvfile(self):
        pre_data = sorted(glob.glob("../../pre_data/*"))
        print("predata:",pre_data)
        dest_dir = f"test/{self.startTime}/camera_result/second_spm/learn{self.learncount}"
        for file in pre_data:
            shutil.copy2(file, dest_dir)

cansat = Cansat()