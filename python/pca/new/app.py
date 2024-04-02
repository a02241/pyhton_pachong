from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from flask import render_template
import os
from flask import Flask, request, send_file
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
import joblib

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
    # 加载训练好的欺诈检测模型
    model = joblib.load('./fraud_detection_model.pkl')

    # 读取上传的Excel文件作为测试数据
    df_test = pd.read_excel(file_path)

    # 对测试数据进行预处理
    # 此处去除个人编码列，该列为个人标识信息，不用于模型预测
    df_test.drop(columns=['个人编码'], inplace=True)
    # 分离出用于模型预测的特征集合
    X_test = df_test.drop(columns=['RES'])

    # 数值特征的预处理步骤
    numeric_features = X_test.select_dtypes(include=['int64', 'float64']).columns
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())  # 数值标准化
    ])

    # 分类特征的预处理步骤
    categorical_features = X_test.select_dtypes(include=['object']).columns
    categorical_transformer = Pipeline(steps=[
        ('encoder', OneHotEncoder(handle_unknown='ignore'))  # 分类编码
    ])

    # 构建列转换处理器，为不同类型特征应用不同的处理
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    # 对测试数据应用预处理步骤
    X_test_preprocessed = preprocessor.fit_transform(X_test)

    # 将预处理后的数据转换成DataFrame格式，以便进行预测
    X_test_preprocessed_df = pd.DataFrame(X_test_preprocessed, columns=X_test.columns)

    # 使用模型进行预测
    y_pred = model.predict(X_test_preprocessed_df)

    # 将预测结果添加到测试数据DataFrame中
    df_test['预测是否欺诈'] = y_pred

    # 保存带有预测结果的文件
    result_file_path = os.path.join('./results', 'result.xlsx')
    df_test.to_excel(result_file_path, index=False)

    # 返回结果文件的路径
    return result_file_path


def run_model():
    # 第1步：加载数据
    df = pd.read_csv('./【东软集团A08】医保特征数据16000（修订版2）.csv', encoding='utf-8')
    imputer = SimpleImputer(strategy='mean')
    df = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
    # 第2步：数据探索
    # 查看数据的前几行进行初步探索
    print(df.head())

    # 检查数据集的大小和缺失值情况
    print(df.shape)
    print(df.isnull().sum())

    # 第3步：数据预处理
    # 删除不需要的列，例如'个人编码'（作为ID的列通常对模型的预测作用不大）
    df.drop(columns=['个人编码'], inplace=True)

    # 分离特征和目标变量
    X = df.drop(columns=['RES'])  # 特征变量
    y = df['RES']  # 目标变量

    # 数值数据的处理
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns  # 选择数值型特征
    numeric_transformer = Pipeline(steps=[
        ('scaler', StandardScaler())  # 标准化处理
    ])

    # 分类型数据的处理，例如'出院诊断病种名称_NN'为分类数据，但注意观察数据是否需要处理
    categorical_features = X.select_dtypes(include=['object']).columns  # 选择分类特征
    categorical_transformer = Pipeline(steps=[
        ('encoder', OneHotEncoder(handle_unknown='ignore'))  # one-hot编码处理
    ])

    # 第4步：特征工程
    # 构建预处理转换器，这里我们搭建了一个包含数值数据和分类数据处理的管道
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    # 第5步：构建模型
    # 定义随机森林模型
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(random_state=42))
    ])

    # 第6步：模型训练与评估
    # 分割数据集为训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 拟合模型
    model.fit(X_train, y_train)

    # 在测试集上做预测
    y_pred = model.predict(X_test)

    # 输出模型评估报告
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Classification Report:\n", classification_report(y_test, y_pred))

    # 第7步：模型保存
    # 将模型保存到本地文件
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
