import logger
from flask import Flask, jsonify, request, send_file
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
import joblib
import os

app = Flask(__name__)

# 设置全局字体为系统内置字体
plt.rcParams['font.family'] = 'Microsoft YaHei'  # 指定字体为微软雅黑,可以根据自己的系统和字体库选择合适的字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

if not os.path.exists('random_forest_model.pkl') or not os.path.exists('预测结果.csv'):
    logger.logger.info('重新训练模型')

    # 读取数据
    df = pd.read_csv('【东软集团A08】医保特征数据16000（修订版2）.csv')
    # 使用SimpleImputer填充缺失值
    imputer = SimpleImputer(strategy='mean')
    df = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)

    # 数据预处理（根据需要进行填充、转换等）
    X = df.drop(['RES'], axis=1)
    feature_names = X.columns
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

    # 保存模型和训练数据以及特征列名称
    model_data = {
        'X': X,
        'model': model,
        'X_train': X_train,
        'X_test': X_test,
        'y_train': y_train,
        'y_test': y_test,
        'X_pca': X_pca,
        'scaler': scaler,
        'pca': pca
    }
    joblib.dump(model_data, 'random_forest_model.pkl')
    model = model_data['model']
    # 对每一条数据进行预测并判断是否骗保
    predictions = []
    print('正在处理预测')
    for _, row in df.iterrows():
        # 对单条数据进行预处理
        row_data = pd.DataFrame(row.drop(['RES'])).T
        row_data.columns = feature_names
        row_data_scaled = scaler.transform(row_data)
        row_data_pca = pca.transform(row_data_scaled)

        # 进行预测
        prediction = model.predict(row_data_pca)
        predictions.append(prediction[0])

    # 将预测结果添加到原始数据集中
    df['预测是否骗保'] = predictions

    # 将结果保存到CSV文件
    df.to_csv('预测结果.csv', index=False)
    print('处理预测完毕，已保存到预测结果.csv中')

else:
    # 加载模型和训练数据以及特征列名称
    logger.logger.info('加载训练模型')
    model_data = joblib.load('random_forest_model.pkl')
    model = model_data['model']
    X_train = model_data['X_train']
    X_test = model_data['X_test']
    y_train = model_data['y_train']
    y_test = model_data['y_test']
    X = model_data['X']
    feature_names = X.columns
    X_pca = model_data['X_pca']
    scaler = model_data['scaler']
    pca = model_data['pca']


@app.route('/predict')
def predict():
    # 模型评估
    y_pred = model.predict(X_test)
    print("混淆矩阵:\n", confusion_matrix(y_test, y_pred))
    print("\n分类报告:\n", classification_report(y_test, y_pred))

    # 特征重要性分析
    pca_feature_names = [f"PC{i + 1}" for i in range(X_pca.shape[1])]
    feature_names_mapping = dict(zip(pca_feature_names, feature_names))
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


@app.route('/download_csv')
def download_csv():
    # 本地CSV文件路径
    csv_path = '预测结果.csv'
    try:
        return send_file(csv_path, as_attachment=True, download_name='file.csv')
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    app.run()
