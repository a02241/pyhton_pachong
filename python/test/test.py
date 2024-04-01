import pandas as pd
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Microsoft YaHei'  # 指定字体为微软雅黑，可以根据自己的系统和字体库选择合适的字体
data = pd.read_csv('【东软集团A08】医保特征数据16000（修订版）.csv')
data.dropna(subset=['出院诊断LENTH_MAX'], inplace=True)  # 删除包含缺失值的行

X = data.iloc[:, 2:80]  # 这里的自变量是在1-25列
y = data.iloc[:, 81]    # 这里的因变量是第26列

pca = PCA()
X_pca = pca.fit_transform(X)

explained_variance_ratio = pca.explained_variance_ratio_
component_names = [f'PC{i+1}' for i in range(len(explained_variance_ratio))]

print("主成分贡献度:")
for i, (label, variance_ratio) in enumerate(zip(component_names, explained_variance_ratio[:11]), start=1):
    print(f"主成分 {label}: {variance_ratio:.4f}")

plt.figure(figsize=(10, 6))
plt.bar(component_names, explained_variance_ratio[:78], alpha=0.7)  # 这里的数字也改为“六”中相同的即可
plt.xlabel('主成分')
plt.ylabel('贡献度')
plt.title('主成分贡献度')
plt.xticks(rotation=30)  # 旋转 x 轴标签
plt.tight_layout()  # 调整布局，确保标签完整显示
plt.show()

# 计算贡献度的累计值
cumulative_variance_ratio = explained_variance_ratio.cumsum()

# 绘制贡献度的累计折线图
plt.figure(figsize=(10, 6))
plt.plot(range(1, len(cumulative_variance_ratio) + 1), cumulative_variance_ratio, marker='o')
plt.xlabel('主成分数量')
plt.ylabel('累计贡献度')
plt.title('贡献度累计折线图')

# 标注主成分的名称
for i, txt in enumerate(component_names[:len(cumulative_variance_ratio)]):
    plt.annotate(txt, (i + 1, cumulative_variance_ratio[i]), fontsize=10)

plt.grid(True)
plt.show()
