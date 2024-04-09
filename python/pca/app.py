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
#
# app = Flask(__name__)
#
# # 设置全局字体为系统内置字体
# plt.rcParams['font.family'] = 'Microsoft YaHei'  # 指定字体为微软雅黑,可以根据自己的系统和字体库选择合适的字体
# plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
#
# if not os.path.exists('random_forest_model.pkl') or not os.path.exists('预测结果.csv'):
#     logger.logger.info('重新训练模型')
#
#     # 读取数据
#     df = pd.read_csv('【东软集团A08】医保特征数据16000（修订版2）.csv')
#     # 使用SimpleImputer填充缺失值
#     imputer = SimpleImputer(strategy='mean')
#     df = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
#
#     # 数据预处理（根据需要进行填充、转换等）
#     X = df.drop(['RES'], axis=1)
#     feature_names = X.columns
#     y = df['RES']
#
#     # 标准化数据
#     scaler = StandardScaler()
#     X_scaled = scaler.fit_transform(X)
#
#     # PCA降维
#     pca = PCA(n_components=0.95)  # 保留95%的方差
#     X_pca = pca.fit_transform(X_scaled)
#
#     # 划分数据集
#     X_train, X_test, y_train, y_test = train_test_split(X_pca, y, test_size=0.2, random_state=42)
#
#     # 建立随机森林模型并训练
#     model = RandomForestClassifier(random_state=42)
#     model.fit(X_train, y_train)
#
#     # 保存模型和训练数据以及特征列名称
#     model_data = {
#         'X': X,
#         'model': model,
#         'X_train': X_train,
#         'X_test': X_test,
#         'y_train': y_train,
#         'y_test': y_test,
#         'X_pca': X_pca,
#         'scaler': scaler,
#         'pca': pca
#     }
#     joblib.dump(model_data, 'random_forest_model.pkl')
#     model = model_data['model']
#     # 对每一条数据进行预测并判断是否骗保
#     predictions = []
#     print('正在处理预测')
#     for _, row in df.iterrows():
#         # 对单条数据进行预处理
#         row_data = pd.DataFrame(row.drop(['RES'])).T
#         row_data.columns = feature_names
#         row_data_scaled = scaler.transform(row_data)
#         row_data_pca = pca.transform(row_data_scaled)
#
#         # 进行预测
#         prediction = model.predict(row_data_pca)
#         predictions.append(prediction[0])
#
#     # 将预测结果添加到原始数据集中
#     df['预测是否骗保'] = predictions
#
#     # 将结果保存到CSV文件
#     df.to_csv('预测结果.csv', index=False)
#     print('处理预测完毕，已保存到预测结果.csv中')
#
# else:
#     # 加载模型和训练数据以及特征列名称
#     logger.logger.info('加载训练模型')
#     model_data = joblib.load('random_forest_model.pkl')
#     model = model_data['model']
#     X_train = model_data['X_train']
#     X_test = model_data['X_test']
#     y_train = model_data['y_train']
#     y_test = model_data['y_test']
#     X = model_data['X']
#     feature_names = X.columns
#     X_pca = model_data['X_pca']
#     scaler = model_data['scaler']
#     pca = model_data['pca']
#
#
# @app.route('/predict')
# def predict():
#     # 模型评估
#     y_pred = model.predict(X_test)
#     print("混淆矩阵:\n", confusion_matrix(y_test, y_pred))
#     print("\n分类报告:\n", classification_report(y_test, y_pred))
#
#     # 特征重要性分析
#     pca_feature_names = [f"PC{i + 1}" for i in range(X_pca.shape[1])]
#     feature_names_mapping = dict(zip(pca_feature_names, feature_names))
#     feature_importances = pd.Series(model.feature_importances_, index=pca_feature_names)
#     feature_importances.sort_values(ascending=False, inplace=True)
#
#     plt.figure(figsize=(20, 24))  # 调整图的大小
#     sns.barplot(x=feature_importances, y=feature_importances.index.map(feature_names_mapping))
#     plt.title("特征重要性（经PCA处理后）")
#     plt.savefig('feature_importance_plot.png')  # 保存图表为PNG文件
#
#     # 输出特征重要性数值
#     print("特征重要性:")
#     print(feature_importances)
#
#     # 将特征重要性数值转换为JSON格式
#     feature_importances_json = feature_importances.to_json()
#     return jsonify(feature_importances_json)
#
#
# @app.route('/download_csv')
# def download_csv():
#     # 本地CSV文件路径
#     csv_path = '预测结果.csv'
#     try:
#         return send_file(csv_path, as_attachment=True, download_name='file.csv')
#     except Exception as e:
#         return str(e)
#
import json

if __name__ == '__main__':
    data = {
        "code": 200,
        "data": {
            "feature_importance": "[{\"Feature\":\"num__月统筹金额_MAX\",\"Importance\":0.0513178432},{\"Feature\":\"num__ALL_SUM\",\"Importance\":0.0425410725},{\"Feature\":\"num__月药品金额_MAX\",\"Importance\":0.0420588128},{\"Feature\":\"num__顺序号_NN\",\"Importance\":0.0366992805},{\"Feature\":\"num__本次审批金额_SUM\",\"Importance\":0.0327076953},{\"Feature\":\"num__月药品金额_AVG\",\"Importance\":0.0277709245},{\"Feature\":\"num__月就诊次数_MAX\",\"Importance\":0.0257374899},{\"Feature\":\"num__药品费发生金额_SUM\",\"Importance\":0.0254232779},{\"Feature\":\"num__月统筹金额_AVG\",\"Importance\":0.0248570204},{\"Feature\":\"num__月就诊天数_AVG\",\"Importance\":0.0247316163},{\"Feature\":\"num__统筹支付金额_SUM\",\"Importance\":0.0246634855},{\"Feature\":\"num__基本统筹基金支付金额_SUM\",\"Importance\":0.023662617},{\"Feature\":\"num__月就诊天数_MAX\",\"Importance\":0.0231492142},{\"Feature\":\"num__月就诊次数_AVG\",\"Importance\":0.0227158646},{\"Feature\":\"num__药品费申报金额_SUM\",\"Importance\":0.0226657328},{\"Feature\":\"num__起付标准以上自负比例金额_SUM\",\"Importance\":0.020925449},{\"Feature\":\"num__就诊次数_SUM\",\"Importance\":0.0194006155},{\"Feature\":\"num__交易时间DD_NN\",\"Importance\":0.019114859},{\"Feature\":\"num__治疗费申报金额_SUM\",\"Importance\":0.0189241326},{\"Feature\":\"num__医院_统筹金_AVG\",\"Importance\":0.0177140412},{\"Feature\":\"num__医院_统筹金_MAX\",\"Importance\":0.0173963727},{\"Feature\":\"num__中成药费发生金额_SUM\",\"Importance\":0.0171903793},{\"Feature\":\"num__药品在总金额中的占比\",\"Importance\":0.0170212899},{\"Feature\":\"num__医院_药品_AVG\",\"Importance\":0.016791049},{\"Feature\":\"num__治疗费用在总金额占比\",\"Importance\":0.0165858015},{\"Feature\":\"num__个人账户金额_SUM\",\"Importance\":0.0165065319},{\"Feature\":\"num__非账户支付金额_SUM\",\"Importance\":0.0163514537},{\"Feature\":\"num__治疗费发生金额_SUM\",\"Importance\":0.0162092849},{\"Feature\":\"num__可用账户报销金额_SUM\",\"Importance\":0.0155279193},{\"Feature\":\"num__医院_药品_MAX\",\"Importance\":0.0154320911},{\"Feature\":\"num__药品费自费金额_SUM\",\"Importance\":0.0153274533},{\"Feature\":\"num__医院_就诊天数_AVG\",\"Importance\":0.0152437916},{\"Feature\":\"num__出院诊断LENTH_MAX\",\"Importance\":0.0149846646},{\"Feature\":\"num__医院_就诊天数_MAX\",\"Importance\":0.0144886828},{\"Feature\":\"num__医用材料发生金额_SUM\",\"Importance\":0.0136733553},{\"Feature\":\"num__个人支付的药品占比\",\"Importance\":0.013496025},{\"Feature\":\"num__检查费申报金额_SUM\",\"Importance\":0.0126727815},{\"Feature\":\"num__检查费发生金额_SUM\",\"Importance\":0.0125548922},{\"Feature\":\"num__一次性医用材料申报金额_SUM\",\"Importance\":0.0118860245},{\"Feature\":\"num__出院诊断病种名称_NN\",\"Importance\":0.0115279373},{\"Feature\":\"num__检查总费用在总金额占比\",\"Importance\":0.0111720835},{\"Feature\":\"num__月就诊医院数_AVG\",\"Importance\":0.011081175},{\"Feature\":\"num__基本个人账户支付_SUM\",\"Importance\":0.0110715855},{\"Feature\":\"num__贵重药品发生金额_SUM\",\"Importance\":0.0107325567},{\"Feature\":\"num__中草药费发生金额_SUM\",\"Importance\":0.0105338914},{\"Feature\":\"num__交易时间YYYYMM_NN\",\"Importance\":0.0076256889},{\"Feature\":\"num__就诊的月数\",\"Importance\":0.0074679179},{\"Feature\":\"num__医疗救助个人按比例负担金额_SUM\",\"Importance\":0.0065731106},{\"Feature\":\"num__一天去两家医院的天数\",\"Importance\":0.0064166401},{\"Feature\":\"num__医用材料费自费金额_SUM\",\"Importance\":0.0062839564},{\"Feature\":\"num__医疗救助医院申请_SUM\",\"Importance\":0.0058502052},{\"Feature\":\"num__医院编码_NN\",\"Importance\":0.0055657555},{\"Feature\":\"num__月就诊医院数_MAX\",\"Importance\":0.0055576516},{\"Feature\":\"num__补助审批金额_SUM\",\"Importance\":0.0053795631},{\"Feature\":\"num__其它发生金额_SUM\",\"Importance\":0.0051365624},{\"Feature\":\"num__民政救助补助_SUM\",\"Importance\":0.0045275104},{\"Feature\":\"num__城乡救助补助金额_SUM\",\"Importance\":0.0041007615},{\"Feature\":\"num__治疗费自费金额_SUM\",\"Importance\":0.0036922183},{\"Feature\":\"num__个人支付治疗费用占比\",\"Importance\":0.0032816812},{\"Feature\":\"num__检查费自费金额_SUM\",\"Importance\":0.0032437269},{\"Feature\":\"num__个人支付检查费用占比\",\"Importance\":0.0029887058},{\"Feature\":\"num__床位费发生金额_SUM\",\"Importance\":0.002363317},{\"Feature\":\"num__贵重检查费金额_SUM\",\"Importance\":0.0023301563},{\"Feature\":\"num__床位费申报金额_SUM\",\"Importance\":0.0022634927},{\"Feature\":\"num__是否挂号\",\"Importance\":0.0017334028},{\"Feature\":\"num__公务员医疗补助基金支付金额_SUM\",\"Importance\":0.0014864709},{\"Feature\":\"num__高价材料发生金额_SUM\",\"Importance\":0.0011633849},{\"Feature\":\"num__BZ_民政救助\",\"Importance\":0.0010623866},{\"Feature\":\"num__起付线标准金额_MAX\",\"Importance\":0.0005968232},{\"Feature\":\"num__城乡优抚补助_SUM\",\"Importance\":0.0002780295},{\"Feature\":\"num__手术费自费金额_SUM\",\"Importance\":0.0002090526},{\"Feature\":\"num__BZ_城乡优抚\",\"Importance\":0.0002037163},{\"Feature\":\"num__手术费发生金额_SUM\",\"Importance\":0.0001521876},{\"Feature\":\"num__手术费申报金额_SUM\",\"Importance\":0.0001466359},{\"Feature\":\"num__其它申报金额_SUM\",\"Importance\":0.0000480253},{\"Feature\":\"num__成分输血申报金额_SUM\",\"Importance\":0.0000227396},{\"Feature\":\"num__残疾军人补助_SUM\",\"Importance\":0.0000084046},{\"Feature\":\"num__住院天数_SUM\",\"Importance\":0.0},{\"Feature\":\"num__交易时间YYYY_NN\",\"Importance\":0.0},{\"Feature\":\"num__最高限额以上金额_SUM\",\"Importance\":0.0}]"
        },
        "message": "success"
    }

    # 解析JSON数据
    # data = json.loads(json_string)
    feature_importance = json.loads(data['data']['feature_importance'])

    # 提取贡献度值
    importance_values = [float(feature['Importance']) for feature in feature_importance]

    # 计算贡献度的平均值
    average_importance = sum(importance_values) / len(importance_values)

    # 统计贡献度高于平均值的特征数量
    count_above_average = sum(1 for value in importance_values if value > average_importance)

    print(f"贡献度均值: {average_importance:.6f}")
    print(f"贡献度高于平均值的特征数量: {count_above_average}")
