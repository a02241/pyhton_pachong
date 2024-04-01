from flask import Flask, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

app = Flask(__name__)

# 设置全局字体为系统内置字体
plt.rcParams['font.family'] = 'Microsoft YaHei'  # 指定字体为微软雅黑，可以根据自己的系统和字体库选择合适的字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
if not os.path.exists('random_forest_model.pkl'):
    # 读取数据
    df = pd.read_csv('【东软集团A08】医保特征数据16000（修订版）.csv')
    df.dropna(subset=['出院诊断LENTH_MAX'], inplace=True)  # 删除包含缺失值的行
    # 数据预处理（根据需要进行填充、转换等）
    X = df.drop(['RES'], axis=1)
    y = df['RES']
    # 标准化数据
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    # PCA降维
    pca = PCA(n_components=0.95)  # 保留95%的方差
    X_pca = pca.fit_transform(X_scaled)
    # 划分数据集
    X_train, X_test, y_train, y_test = train_test_split(X_pca, y, test_size=0.2, random_state=42)

    # 建立随机森林模型并训练
    model = RandomForestClassifier(random_state=42)
    model.fit(X_train, y_train)
    # 保存模型
    joblib.dump(model, 'random_forest_model.pkl')
else:
    # 加载模型
    model = joblib.load('random_forest_model.pkl')


@app.route('/test')
def hello_world():
    # 模型评估
    y_pred = model.predict(X_test)
    print("混淆矩阵:\n", confusion_matrix(y_test, y_pred))
    print("\n分类报告:\n", classification_report(y_test, y_pred))
    # 特征重要性分析
    original_feature_names = X.columns
    pca_feature_names = [f"PC{i + 1}" for i in range(X_pca.shape[1])]
    feature_names_mapping = dict(zip(pca_feature_names, original_feature_names))
    feature_importances = pd.Series(model.feature_importances_, index=pca_feature_names)
    feature_importances.sort_values(ascending=False, inplace=True)

    plt.figure(figsize=(20, 24))  # 调整图的大小
    sns.barplot(x=feature_importances, y=feature_importances.index.map(feature_names_mapping))
    plt.title("特征重要性（经PCA处理后）")
    plt.savefig('feature_importance_plot.png')  # 保存图表为PNG文件

    # 输出特征重要性数值
    print("特征重要性:")
    print(feature_importances)

    # 将特征重要性数值转换为JSON格式
    feature_importances_json = feature_importances.to_json()
    return jsonify(feature_importances_json)


if __name__ == '__main__':
    app.run()
