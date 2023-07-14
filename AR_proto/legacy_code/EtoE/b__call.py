from concurrent.futures import ProcessPoolExecutor
import numpy as np
from datetime import datetime
from glob import glob
import time
import re

from b_executor import Bspm

# 全特徴画像学習済みdict
dicts = {}

'''
Cansatの大元のmain.pyで以下を記述できる場合にはこのプログラム
マルチプロセスによる並行処理
以下を記述できない場合やb_executor.pyを呼び出すファイルが__name__=="__main__"ではない場合は不可
'''
# 開発段階ではムービーの画像パスを取得
import_paths = glob("../a_prepare/ac_pictures/aca_normal/movie_1/*.jpg")
import_paths = import_paths[:100]
for n in range(len(import_paths)):
    start_time = time.time()
    importPath = f"../a_prepare/ac_pictures/aca_normal/movie_1/frame_{n}.jpg".replace("\\","/")
    '''
    ここまでは開発段階のみ使用
    '''


    # もし別の保存場所指定したい場合
    savedir = "b-data"
    # ステートはいずれ数値？
    if n == 0:
        learn_state = True
    else:
        learn_state = False
    # 写真の時刻（写真識別番号）
    now = str(datetime.now())[:19].replace(" ","_").replace(":","-")
    # 各特徴画像学習済み辞書dict
    dict_lists = []
    # 特徴量dict
    values_list = []
    # c_cpmで使用する特徴量グループ
    feature_values = {}

    bspm = Bspm(saveDir=savedir)
    if __name__ == "__main__":
        with ProcessPoolExecutor(max_workers=8) as executor:
            normalRGB = executor.submit(bspm.mainExecutor,learn_state,"normalRGB",now,dicts,importPath)
            #vari = executor.submit(bspm.mainExecutor,learn_state,"vari",now,dicts,importPath)
            #rgbvi = executor.submit(bspm.mainExecutor,learn_state,"rgbvi",now,dicts,importPath)
            #grvi = executor.submit(bspm.mainExecutor,learn_state,"grvi",now,dicts,importPath)
            #ior = executor.submit(bspm.mainExecutor,learn_state,"ior",now,dicts,importPath)
            enphasis = executor.submit(bspm.mainExecutor,learn_state,"enphasis",now,dicts,importPath)
            edge = executor.submit(bspm.mainExecutor,learn_state,"edge",now,dicts,importPath)
            hsv = executor.submit(bspm.mainExecutor,learn_state,"hsv",now,dicts,importPath)
            r = executor.submit(bspm.mainExecutor,learn_state,"r",now,dicts,importPath)
        with ProcessPoolExecutor(max_workers=8) as executor:
            b = executor.submit(bspm.mainExecutor,learn_state,"g",now,dicts,importPath)
            g = executor.submit(bspm.mainExecutor,learn_state,"b",now,dicts,importPath)
            rb = executor.submit(bspm.mainExecutor,learn_state,"rb",now,dicts,importPath)
            gb = executor.submit(bspm.mainExecutor,learn_state,"gb",now,dicts,importPath)
            rg = executor.submit(bspm.mainExecutor,learn_state,"rg",now,dicts,importPath)

        if not learn_state:
            values_list.append(normalRGB.result()[0])
            #values_list.append(vari.result()[0])
            #values_list.append(rgbvi.result()[0])
            #values_list.append(grvi.result()[0])
            #values_list.append(ior.result()[0])
            values_list.append(enphasis.result()[0])
            values_list.append(edge.result()[0])
            values_list.append(hsv.result()[0])
            values_list.append(r.result()[0])
            values_list.append(g.result()[0])
            values_list.append(b.result()[0])
            values_list.append(rb.result()[0])
            values_list.append(gb.result()[0])
            values_list.append(rg.result()[0])
            for value in values_list:
                feature_values[[key for key in value.keys()][0]] = value[[key for key in value.keys()][0]]
            
        else:
            dict_lists.append(normalRGB.result()[1])
            #dict_lists.append(vari.result()[1])
            #dict_lists.append(rgbvi.result()[1])
            #dict_lists.append(grvi.result()[1])
            #dict_lists.append(ior.result()[1])
            dict_lists.append(enphasis.result()[1])
            dict_lists.append(edge.result()[1])
            dict_lists.append(hsv.result()[1])
            dict_lists.append(r.result()[1])
            dict_lists.append(g.result()[1])
            dict_lists.append(b.result()[1])
            dict_lists.append(rb.result()[1])
            dict_lists.append(gb.result()[1])
            dict_lists.append(rg.result()[1])
            for LD in dict_lists:
                dicts[[key for key in LD.keys()][0]] = LD[[key for key in LD.keys()][0]]
            

    if not learn_state:
        np.savez_compressed(savedir + f"/bcca_secondinput/"+now,array_1=np.array([feature_values]))
        #with open(saveDir + f"/bcca_secondinput/"+now, "wb") as tf:
        #    pickle.dump(feature_values, tf)
        end_time = time.time()
        
        print(f"\n\n==={now}_data was evaluated===\nFRAME number is {n}.\nIt cost {end_time-start_time} seconds.\n\n")