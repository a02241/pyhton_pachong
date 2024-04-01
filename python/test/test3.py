import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# 读取数据
plt.rcParams['font.family'] = 'Microsoft YaHei'  # 指定字体为微软雅黑，可以根据自己的系统和字体库选择合适的字体
data = pd.read_csv('【东软集团A08】医保特征数据16000（修订版）.csv')
data.dropna(subset=['出院诊断LENTH_MAX'], inplace=True)  # 删除包含缺失值的行
# 删除“个人编码”列
data = data.drop(columns=['个人编码'])
# 数据预处理
X = data.drop(['RES'], axis=1)  # 去除目标变量
y = data['RES']

# 数据标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 主成分分析
# pca = PCA()
# X_pca = pca.fit_transform(X_scaled)

# # 绘制散点图
# plt.figure(figsize=(10, 6))
# plt.scatter(X_pca[:, 0], X_pca[:, 1], c=y, cmap='viridis', alpha=0.5)
# plt.xlabel('主成分 1')
# plt.ylabel('主成分 2')
# plt.colorbar()
# plt.title('主成分分析的散点图')
# plt.show()
#
# # 绘制主成分得分系数图
# plt.figure(figsize=(12, 20))
# components = range(1, len(pca.explained_variance_ratio_) + 1)
# plt.barh(components, pca.explained_variance_ratio_, tick_label=X.columns)
# plt.xlabel('方差比例')
# plt.ylabel('特征列')
# plt.title('主成分方差比例')
# plt.show()
#
# # 降维图
# plt.figure(figsize=(10, 6))
# plt.plot(np.cumsum(pca.explained_variance_ratio_))
# plt.xlabel('成分数量')
# plt.ylabel('累计解释方差')
# plt.title('累计解释方差与成分数量的关系')
# plt.show()

# 主成分分析
pca = PCA()
# X_pca = pca.fit_transform(X_scaled)

pca.fit(X)

print(pca.components_)

print('----------------------')
print(pca.explained_variance_ratio_)

print('====================')
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
print(X_scaled)
