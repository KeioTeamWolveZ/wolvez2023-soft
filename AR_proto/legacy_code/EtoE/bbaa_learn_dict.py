import numpy as np
from spmimage.feature_extraction.image import extract_simple_patches_2d
from sklearn.preprocessing import StandardScaler
from spmimage.decomposition import KSVD

class LearnDict():
    patch_size=(5,5)
    n_components=7
    transform_n_nonzero_coefs=3
    max_iter=15
    def __init__(self, img_part:np.ndarray):
        self.train_img = img_part
        self.Y = self.img_to_Y(self.train_img, self.patch_size)
    
    def generate(self):
        self.D, self.ksvd = self.__generate_dict(Y=self.Y, n_components=self.n_components,
                                                 transform_n_nonzero_coefs=self.transform_n_nonzero_coefs, max_iter=self.max_iter)
        return self.D, self.ksvd
    
    def img_to_Y(self, train_img, patch_size=(5,5)):
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