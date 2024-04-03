from flask import render_template
import os
from flask import Flask, request, send_file
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, roc_curve, auc
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 实例化 Flask 应用，设置模板文件夹为当前文件目录
app = Flask(__name__, template_folder=os.path.dirname(__file__))


# 定义上传文件的路由，只允许 POST 方法
@app.route('/upload', methods=['POST'])
def upload():
    # 检查请求中是否包含文件
    if 'file' not in request.files:
        return "没有上传文件"  # 如果没有文件，返回提示信息

    file = request.files['file']  # 获取上传的文件

    # 检查文件名是否为空（即没有选择文件）
    if file.filename == '':
        return "文件名为空"  # 如果文件名为空，返回提示信息

    # 定义文件保存路径，将文件保存在服务器的'./uploads'目录下
    file_path = os.path.join('./uploads', file.filename)

    # 保存上传的文件到指定路径
    file.save(file_path)

    # 处理上传的文件，并获取处理后文件的路径
    result_file_path = process_file(file_path)

    # 返回处理后的文件给用户，允许用户下载该文件
    return send_file(result_file_path, as_attachment=True, download_name='result.xlsx')


# 定义根路由，展示主页
@app.route('/')
def home():
    return render_template('index.html')


# 定义文件处理函数
def process_file(file_path):
    print('正在加载模型')
    # 加载训练好的欺诈检测模型
    model = joblib.load('./fraud_detection_model.pkl')

    # 读取上传的Excel文件作为测试数据
    df_test = pd.read_excel(file_path)

    # 对测试数据进行预处理
    # 此处去除个人编码列，该列为个人标识信息，不用于模型预测
    df_test.drop(columns=['个人编码'], inplace=True)
    # 分离出用于模型预测的特征集合
    X_test = df_test.drop(columns=['RES'])

    # 使用模型进行预测
    y_pred = model.predict(X_test)

    # 将预测结果添加到测试数据DataFrame中
    df_test['预测是否欺诈'] = y_pred

    # 保存带有预测结果的文件
    result_file_path = os.path.join('./results', 'result.xlsx')
    df_test.to_excel(result_file_path, index=False)
    print('模型预测完毕')
    # 返回结果文件的路径
    return result_file_path

# 设置全局字体为系统内置字体
plt.rcParams['font.family'] = 'Microsoft YaHei'  # 指定字体为微软雅黑,可以根据自己的系统和字体库选择合适的字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
def run_model():
    # 第1步:加载数据
    df = pd.read_csv('./【东软集团A08】医保特征数据16000（修订版）.csv', encoding='utf-8')
    imputer = SimpleImputer(strategy='mean')
    df = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)

    # 第2步:数据探索
    print(df.head())
    print(df.shape)
    print(df.isnull().sum())

    # 第3步:数据预处理
    df.drop(columns=['个人编码'], inplace=True)
    X = df.drop(columns=['RES'])
    y = df['RES']

    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())
    ])

    categorical_features = X.select_dtypes(include=['object']).columns
    categorical_transformer = Pipeline(steps=[
        ('encoder', OneHotEncoder(handle_unknown='ignore'))
    ])

    # 第4步:特征工程
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    # 第5步:构建模型
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(random_state=42))
    ])

    # 第6步:模型训练与评估
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("准确率:", accuracy_score(y_test, y_pred))
    print("分类报告:\n", classification_report(y_test, y_pred))

    # 绘制特征重要性图
    feature_importances = model.named_steps['classifier'].feature_importances_
    feature_names = X.columns

    plt.figure(figsize=(10, 15))
    plt.barh(range(len(feature_importances)), feature_importances, align='center')
    plt.yticks(range(len(feature_names)), feature_names)
    plt.xlabel('特征重要性')
    plt.ylabel('特征')
    plt.title('特征重要性图')
    plt.tight_layout()
    plt.savefig('feature_importance.png')
    plt.show()

    # 绘制混淆矩阵
    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('预测标签')
    plt.ylabel('真实标签')
    plt.title('混淆矩阵')
    plt.savefig('confusion_matrix.png')
    plt.show()

    # 绘制ROC曲线和AUC值
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f'AUC = {roc_auc:.2f}')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('假正率')
    plt.ylabel('真正率')
    plt.title('ROC曲线')
    plt.legend(loc='lower right')
    plt.savefig('roc_curve.png')
    plt.show()

    # 第7步:模型保存
    joblib.dump(model, './fraud_detection_model.pkl')


if __name__ == '__main__':
    # 检查并创建必要的目录
    if not os.path.exists('./fraud_detection_model.pkl'):
        run_model()
    if not os.path.exists('./uploads'):
        os.makedirs('./uploads')
    if not os.path.exists('./results'):
        os.makedirs('./results')
    # 运行 Flask 应用
    app.run()
