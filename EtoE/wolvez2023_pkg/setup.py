from setuptools import setup, find_packages

setup(
    name='Wolvez2023',  # パッケージ名（pip listで表示される）
    version="0.1.1",  # バージョン
    description="Package for Cansat in Wolve'Z-2023",  # 説明
    author='MasatoInoue',  # 作者名
    packages=find_packages(),  # 使うモジュール一覧を指定する
    license='MIT'  # ライセンス
)
