import re
import shutil

from flask import render_template, jsonify, Flask, request, send_file
import logging
from sklearn.feature_selection import SelectFromModel
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
import os
import seaborn as sns
from flask_cors import CORS
app = Flask(__name__,
            static_folder='./static',  # 设置静态文件夹目录
            template_folder="./static",
            static_url_path="")  # 设置vue编译输出目录dist文件夹，为Flask模板文件目录

CORS(app, resources=r'/*')
app.config['TEMPLATES_FOLDER'] = 'templates'


# 如果你没有使用 Matplotlib 或 Seaborn 则以下两行可以注释掉
# plt.rcParams['font.family'] = 'Microsoft YaHei'
# plt.rcParams['axes.unicode_minus'] = False

@app.route('/upload', methods=['GET', 'POST'])
@app.route('/api/upload', methods=['GET', 'POST'])
def upload():
    # 检查文件是否在请求中
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '没有上传文件'})
    file = request.files['file']
    # 如果未提供model_name，则默认为"医疗保险欺诈识别监测模型1"
    model_name = request.form.get('model_name', '医疗保险欺诈识别监测模型1') or request.args.get('model_name',
                                                                                                 '医疗保险欺诈识别监测模型1')

    # 文件检验
    if not file.filename:
        return jsonify({'code': 400, 'message': '文件名为空'})
    if not file.filename.lower().endswith(('.xlsx', '.csv')):
        return jsonify({'code': 400, 'message': '上传的文件必须是Excel文件(.xlsx)或CSV文件(.csv)'})

    # 保存文件
    model_path = os.path.join(model_dir, model_name, 'uploads')
    os.makedirs(model_path, exist_ok=True)  # 保证目录存在
    file_path = os.path.join(model_path, file.filename)
    file.save(file_path)

    # 文件处理与反馈
    try:
        if file_path.lower().endswith('.xlsx'):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path, encoding='utf-8')
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'num_rows': df.shape[0],
                'num_columns': df.shape[1],
                'file_path': file_path
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': f'读取文件时发生错误: {e}'})


@app.route('/api/process_missing_value', methods=['GET', 'POST'])
@app.route('/process_missing_value', methods=['GET', 'POST'])
def process_missing_value():
    file_path = request.form.get("file_path") or request.args.get("file_path")
    missing_value = request.form.get("missing_value") or request.args.get("missing_value")

    if not file_path:
        return jsonify({'code': 400, 'message': '路径、文件名称错误'})

    if file_path.lower().endswith('.xlsx'):
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path, encoding='utf-8')

    if missing_value not in ['mean', 'median', 'most_frequent']:
        return jsonify({
            'code': 400,
            'message': 'Invalid missing_value. Allowed values are: mean, median, most_frequent'
        })

    # 处理缺失值
    logging.info('处理缺失值')
    imputer = SimpleImputer(strategy=missing_value)
    df = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)

    # 处理异常值
    logging.info('处理异常值')
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

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    preprocessor.fit(X)

    selector = SelectFromModel(estimator=RandomForestClassifier(random_state=42), threshold='mean')
    selector.fit(preprocessor.transform(X), y)

    preprocessed_feature_names = preprocessor.get_feature_names_out()
    feature_importances = selector.estimator_.feature_importances_

    feature_importance_df = pd.DataFrame({'Feature': preprocessed_feature_names, 'Importance': feature_importances})
    feature_importance_df = feature_importance_df.sort_values('Importance', ascending=False)

    feature_importance_json = feature_importance_df.to_json(orient='records', force_ascii=False).encode('utf-8')

    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'feature_importance': feature_importance_json.decode('utf-8')
        }
    })


# 新建模型的路由，创建模型所需的文件夹结构
@app.route('/api/new_model', methods=['GET', 'POST'])
@app.route('/new_model', methods=['GET', 'POST'])
def new_model():
    model_name = request.args.get("model_name")
    os.makedirs(model_dir, exist_ok=True)  # 确保模型根目录存在
    model_list = [name for name in os.listdir(model_dir) if os.path.isdir(os.path.join(model_dir, name))]

    if not model_name:
        # 匹配模型名称中的数字，找到最大的编号
        pattern = r"医疗保险欺诈识别监测模型(\d+)"
        max_num = 0
        for name in model_list:
            match = re.match(pattern, name)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
        # 生成新的模型名称
        model_name = f"医疗保险欺诈识别监测模型{max_num + 1}"

    # 创建模型的相关目录
    new_model_dir = os.path.join(model_dir, model_name)
    os.makedirs(os.path.join(new_model_dir, 'uploads'), exist_ok=True)
    os.makedirs(os.path.join(new_model_dir, 'results'), exist_ok=True)

    return jsonify({'code': 200, 'message': '新模型文件夹创建成功', 'model_name': model_name})


@app.route('/api/process_file', methods=['GET', 'POST'])  # 支持GET和POST请求
@app.route('/process_file', methods=['GET', 'POST'])  # 支持GET和POST请求
def process_file():
    # 获取请求参数
    file_path = request.form.get("file_path") or request.args.get("file_path")
    model_name = request.form.get("model_name") or request.args.get("model_name")

    # 验证参数
    if not file_path or not model_name:
        return jsonify({'code': 400, 'message': '路径、文件名称或模型名称错误'})

    logging.info('构建模型文件路径并加载模型')
    model_file_path = os.path.join('./model', model_name, 'fraud_detection_model.pkl')
    if not os.path.exists(model_file_path):
        return jsonify({'code': 404, 'message': '模型文件不存在'})
    model = joblib.load(model_file_path)

    # 验证并读取测试数据文件
    if not os.path.exists(file_path):
        return jsonify({'code': 404, 'message': '测试文件不存在'})
    if file_path.endswith('.xlsx'):
        df_test = pd.read_excel(file_path)
    elif file_path.endswith('.csv'):
        df_test = pd.read_csv(file_path)
    else:
        return jsonify({'code': 400, 'message': '测试文件类型错误'})

    logging.info('预处理测试数据并进行预测')
    # 保留个人编码和RES列，如果存在
    X_test = df_test.drop(columns=['RES'], errors='ignore')
    y_pred = model.predict(X_test)
    df_test['预测是否欺诈'] = y_pred  # 添加预测结果到新列

    # 保存结果文件
    logging.info('保存结果文件')
    results_dir = os.path.join('./model', model_name, 'results')
    os.makedirs(results_dir, exist_ok=True)
    result_file_path = os.path.join(results_dir, 'processed_result.xlsx')
    df_test.to_excel(result_file_path, index=False)

    # 返回文件供下载
    try:
        return send_file(result_file_path, as_attachment=True, download_name='processed_result.xlsx')
    except Exception as e:
        logging.error(f'文件发送失败: {str(e)}')
        return jsonify({'code': 500, 'message': f'文件发送失败: {str(e)}'})


@app.route('/api/run_model', methods=['GET', 'POST'])
@app.route('/run_model', methods=['GET', 'POST'])
def run_model():
    logging.info('正在加载模型')
    """
    运行模型：加载数据，处理缺失值，训练模型，并评估模型性能。
    """
    # 获取请求参数
    file_path = request.form.get("file_path") or request.args.get("file_path")
    model_name = request.form.get("model_name") or request.args.get("model_name")
    random_state = int(request.form.get("random_state", 42))
    test_size = float(request.form.get("test_size", 0.2))
    missing_value_strategy = request.form.get("missing_value", "mean")

    logging.info(file_path)
    # 验证文件类型并读取数据
    if str(file_path).endswith('.xlsx'):
        df = pd.read_excel(file_path)
    elif str(file_path).endswith('.csv'):
        df = pd.read_csv(file_path, encoding='utf-8')
    else:
        return jsonify({'code': 400, 'message': '文件类型错误'})

    if model_name is None:
        return jsonify({'code': 400, 'message': '模型路径不能为空'})

    # 处理缺失值
    logging.info('处理缺失值')
    if missing_value_strategy in ['mean', 'median', 'most_frequent']:
        imputer = SimpleImputer(strategy=missing_value_strategy)
        df = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
    else:
        return jsonify({'code': 400, 'message': '无效的缺失值处理策略'})

    # 准备数据
    if '个人编码' in df.columns:
        df.drop(columns=['个人编码'], inplace=True)
    X = df.drop(columns=['RES'])
    y = df['RES']

    # 定义数据预处理和特征选择流程
    logging.info('定义数据预处理和特征选择流程')
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns
    categorical_features = X.select_dtypes(include=['object']).columns
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])

    # 构建模型
    logging.info('构建模型')
    model = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(random_state=random_state))
    ])

    # 拆分数据集
    logging.info('拆分数据集')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    # 训练模型
    logging.info('训练模型')
    model.fit(X_train, y_train)

    # 保存模型
    logging.info('保存模型')
    os.makedirs(model_name, exist_ok=True)
    joblib.dump(model, os.path.join(model_name, 'fraud_detection_model.pkl'))

    # 评估模型
    logging.info('进行模型评估')
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    feature_importances = model.named_steps['classifier'].feature_importances_
    cm = confusion_matrix(y_test, y_pred)
    # cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    roc_auc = auc(fpr, tpr)

    # 构建响应数据
    result = {
        'accuracy': accuracy,
        'classification_report': report,
        'feature_importances': feature_importances.tolist(),
        'confusion_matrix': cm.tolist(),
        'roc_curve': {
            'fpr': fpr.tolist(),
            'tpr': tpr.tolist(),
            'auc': roc_auc
        }
    }

    return jsonify({'code': 200, 'message': '模型运行成功', 'data': result})


@app.route('/api/model_list', methods=['GET', 'POST'])
@app.route('/model_list', methods=['GET', 'POST'])
def chose_model():
    os.makedirs(model_dir, exist_ok=True)
    model_list = [name for name in os.listdir(model_dir) if os.path.isdir(os.path.join(model_dir, name))]
    return jsonify(model_list)


@app.route("/api/delete_model", methods=['GET', 'POST'])
@app.route("/delete_model", methods=['GET', 'POST'])
def delete_model():
    model_name = request.form.get("model_name") or request.args.get("model_name")

    if not model_name:
        return jsonify({"error": "model_name is required"}), 400

    model_path = os.path.join(model_dir, model_name)

    if not os.path.exists(model_path):
        return jsonify({"error": f"Model '{model_name}' does not exist"}), 404

    try:
        shutil.rmtree(model_path)
        return jsonify({"message": f"Model '{model_name}' deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def run_default_model(path):
    plt.rcParams['font.family'] = 'Microsoft YaHei'
    plt.rcParams['axes.unicode_minus'] = False
    # 第1步:加载数据
    logging.info('加载数据')
    df = pd.read_csv('./static/【东软集团A08】医保特征数据16000（修订版）.csv', encoding='utf-8')
    imputer = SimpleImputer(strategy='mean')
    df = pd.DataFrame(imputer.fit_transform(df), columns=df.columns)
    # 第2步:数据探索
    logging.info('数据探索')
    logging.info(df.head())
    logging.info(df.shape)
    logging.info(df.isnull().sum())
    # 第3步:数据预处理
    logging.info('数据预处理')
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
    logging.info('特征工程')
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    # 第5步:特征选择
    logging.info('特征选择')
    selector = SelectFromModel(estimator=RandomForestClassifier(random_state=42), threshold='mean')
    # 第6步:构建模型
    logging.info('构建模型')
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('selector', selector),
        ('classifier', RandomForestClassifier(random_state=42))
    ])
    # 第7步:模型训练与评估
    logging.info('模型训练与评估')
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    # 调整分类阈值以提高召回率
    # 评估模型
    print("准确率:", accuracy_score(y_test, y_pred))
    print("分类报告:\n", classification_report(y_test, y_pred))
    # # 调整分类阈值以提高召回率
    # y_pred_proba = model.predict_proba(X_test)[:, 1]
    # y_pred_new = (y_pred_proba >= 0.4).astype(int)
    # print("调整分类阈值后的分类报告:\n", classification_report(y_test, y_pred_new))
    # 生成分类报告
    report = classification_report(y_test, y_pred, output_dict=True)
    # 将分类报告转换为DataFrame
    df_report = pd.DataFrame(report).transpose()
    # 创建一个新的图形和轴
    fig, ax = plt.subplots(figsize=(8, 6))
    # 将DataFrame绘制为表格
    table = ax.table(cellText=df_report.values, colLabels=df_report.columns, rowLabels=df_report.index, loc='center',
                     cellLoc='center')
    # 设置表格的样式
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.2)
    # 隐藏轴的边框和刻度
    ax.axis('off')
    # 调整布局以避免截断文本
    plt.tight_layout()
    # 将图形保存为PNG文件
    plt.savefig('{}/classification_report_table.png'.format(path))
    # 显示图形(可选)
    # plt.show()
    # 绘制特征重要性图
    # 假设preprocessor是你的ColumnTransformer实例
    # 假设selector是SelectFromModel实例，通过它进行了特征选择
    # 注意：如果你的pipeline没有使用SelectFromModel进行特征选择，那么下面的selector相关代码可以省略

    # 获取通过ColumnTransformer预处理后的特征名称
    preprocessed_feature_names = preprocessor.get_feature_names_out()

    # 如果使用了特征选择，进一步筛选被选中的特征
    if 'selector' in model.named_steps:
        selected_mask = model.named_steps['selector'].get_support()
        selected_feature_names = preprocessed_feature_names[selected_mask]
    else:
        selected_feature_names = preprocessed_feature_names

    # 获取特征重要性并与选中的特征名称匹配
    feature_importances = model.named_steps['classifier'].feature_importances_
    plt.figure(figsize=(10, 10))  # 根据特征数量调整图的高度
    plt.barh(range(len(feature_importances)), feature_importances, align='center')
    plt.yticks(range(len(selected_feature_names)), selected_feature_names)
    plt.xlabel('特征重要性')
    plt.ylabel('特征')
    plt.title('特征重要性图')
    plt.tight_layout()
    plt.savefig('{}/feature_importance.png'.format(path))
    # plt.show()

    # 绘制混淆矩阵
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('预测标签')
    plt.ylabel('真实标签')
    plt.title('混淆矩阵')
    plt.savefig('{}/confusion_matrix.png'.format(path))
    # plt.show()
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
    plt.savefig('{}/roc_curve.png'.format(path))
    # plt.show()
    # 第8步:模型保存
    logging.info('第8步:模型保存')
    joblib.dump(model, '{}/fraud_detection_model.pkl'.format(path))


@app.route('/')
def index():
    return render_template('index.html')


model_dir = './model'
if __name__ == '__main__':
    # 检查并创建必要的目录
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    if not os.path.exists('{}/医疗保险欺诈识别监测模型1'.format(model_dir)):
        os.makedirs('{}/医疗保险欺诈识别监测模型1'.format(model_dir))
    if not os.path.exists('{}/医疗保险欺诈识别监测模型1/fraud_detection_model.pkl'.format(model_dir)):
        run_default_model('{}/医疗保险欺诈识别监测模型1'.format(model_dir))
    if not os.path.exists('{}/医疗保险欺诈识别监测模型1/uploads'.format(model_dir)):
        os.makedirs('{}/医疗保险欺诈识别监测模型1/uploads'.format(model_dir))
    if not os.path.exists('{}/医疗保险欺诈识别监测模型1/results'.format(model_dir)):
        os.makedirs('{}/医疗保险欺诈识别监测模型1/results'.format(model_dir))
    app.run(host='0.0.0.0', port=5000, debug=True)
