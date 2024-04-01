import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from factor_analyzer import FactorAnalyzer

# 读取数据
ybdf = pd.read_csv('【东软集团A08】医保特征数据16000（修订版）.csv')
ybdf.dropna(subset=['出院诊断LENTH_MAX'], inplace=True)  # 删除包含缺失值的行
ybdf = ybdf.drop(columns=['个人编码'])
# 查看数据框的前几行
print(ybdf.head())

# 检查是否有缺失值
print(ybdf.isnull().values.any())

# 删除含有缺失值的行
ybdf = ybdf.dropna()

# 删除相关性较强的变量
unique_counts = ybdf.apply(lambda x: len(x.unique()))
high_corr_cols = unique_counts[unique_counts == 1].index
ybdf = ybdf.drop(columns=high_corr_cols)

# 主成分分析
X = ybdf.iloc[:, :-1].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 碎石图
fa = FactorAnalyzer(rotation='varimax')
fa.fit(X_scaled)
ev, v = fa.get_eigenvalues()
plt.scatter(range(1, len(ev) + 1), ev)
plt.plot(range(1, len(ev) + 1), ev, marker='o', color='r')
plt.title('Scree Plot')
plt.xlabel('Factors')
plt.ylabel('Eigenvalue')
plt.grid()
plt.show()

# 确定主成分的个数
pca = PCA(n_components=40)
principalComponents = pca.fit_transform(X_scaled)

# 查看主成分得分
principal_df = pd.DataFrame(data=principalComponents, columns=[f'PC{i}' for i in range(1, pca.n_components_ + 1)])
print(principal_df.head())

# 主成分得分的系数
loadings = pd.DataFrame(pca.components_.T, columns=[f'PC{i}' for i in range(1, pca.n_components_ + 1)], index=ybdf.columns[:-1])
print(loadings)

loadings.to_csv('主成分得分的系数.txt', header=True, index=True, sep='\t')