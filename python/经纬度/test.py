import json
import time

import pandas as pd
from shapely.geometry import Point, Polygon
from shapely.geometry import Point, LineString, shape
from sqlalchemy import create_engine
from pypinyin import lazy_pinyin

engine = create_engine('mysql+pymysql://sys_admin:Mysql_2023!@10.26.39.12/public_interface')
import os
import datetime


def load_point_sqlserver():
    query = "select location,longitude,latitude from public_interface.ct_addr_location_label where status = 0"
    result = pd.read_sql(query, engine)
    return result


def update(location):
    query = "update public_interface.ct_addr_location_label set status = 1 where location = '{}'" \
        .format(location)
    engine.execute(query)


# 读取geojson
def read_geojson(url):
    # 读取GeoJSON数据
    with open(url, encoding='utf-8') as f:
        geojson = json.load(f)
    return geojson


def check_point_in_range_geojson(longitude, latitude, geojson):
    # 指定坐标点
    point = Point(longitude, latitude)

    # 遍历所有特性
    for feature in geojson["features"]:
        # 获取多边形坐标
        # polygon = Polygon(feature["geometry"]["coordinates"])
        # print(feature["geometry"]["coordinates"])
        polygon = Polygon(feature["geometry"]["coordinates"][0])

        # 判断坐标点是否在当前多边形内
        if polygon.contains(point):
            return 1

    # 若遍历了所有多边形仍未找到包含此点的多边形，则返回9
    return 9


def get_geojson_files(folder_path):
    file_paths = []
    file_names = []
    file_real_names = []
    # 使用递归遍历文件夹下的所有文件
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".geojson"):
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
                file_name = os.path.splitext(file)[0]  # 去掉文件后缀
                file_real_names.append(file_name)
                pinyin_name = ''.join([p[0] for p in lazy_pinyin(file_name) if p.isalpha()])  # 只保留拼音首字母
                file_names.append(pinyin_name)
    return file_paths, file_names, file_real_names


def run():
    folder_path = "图片文件/new"
    # folder_path = "/home/nbippc/geojson"

    # 调用函数获取所有的 GeoJSON 文件路径和文件名称
    geojson_files, geojson_names, file_real_names = get_geojson_files(folder_path)
    print(geojson_names)

    print('读取数据中')
    result = load_point_sqlserver()
    print('读取数据完毕')
    # 打印所有的 GeoJSON 文件路径
    column_comments = ['creditcode', '经度', '维度', '地址']  # 填入字段的注释信息
    # 获取 DataFrame 的字段名称和注释
    column_names = result.columns.tolist()
    columns_definition = []
    for column, comment in zip(column_names, column_comments):
        column_definition = f"{column} text COMMENT '{comment}'"
        columns_definition.append(column_definition)
    # 构建 CREATE TABLE 语句的字段定义部分
    start_time = datetime.datetime.now()  # 记录循环开始时间
    for i in range(len(geojson_files)):
        print("文件路径: ", geojson_files[i])
        geojson = read_geojson(geojson_files[i])
        print("文件名称: ", file_real_names[i])
        print("文件名称缩写: ", geojson_names[i])
        column_comments.append(file_real_names[i])
        column_definition = f"{str(file_real_names[i]).replace(' ', '')} int COMMENT '{file_real_names[i]}'"
        columns_definition.append(column_definition)

        loop_start_time = datetime.datetime.now()  # 记录此次循环的开始时间

        result[str(file_real_names[i]).replace(' ', '')] = result.apply(
            lambda row: check_point_in_range_geojson(row['longitude'], row['latitude'], geojson),
            axis=1)

        loop_end_time = datetime.datetime.now()  # 记录此次循环的结束时间
        loop_time_taken = loop_end_time - loop_start_time  # 计算此次循环的耗时
        print("第{}次循环耗时: {}".format(i + 1, loop_time_taken))

        print(file_real_names[i], ' 清洗完毕,第{},总数量{}'.format(i + 1, len(geojson_files)))

    end_time = datetime.datetime.now()  # 记录循环结束时间
    time_taken = end_time - start_time  # 计算总耗时
    print("总耗时: ", time_taken)

    # 获取 DataFrame 的字段名称和注释
    column_names = result.columns.tolist()

    # 构建完整的 CREATE TABLE 语句
    table_name = 'temp_credit_lonlat_result2'
    create_table_sql = f"CREATE TABLE {table_name} ({', '.join(columns_definition)})"

    print(create_table_sql)
    # 执行 CREATE TABLE 语句
    # with engine.connect() as connection:
    #     connection.execute(create_table_sql)
    print('插入数据')
    result.to_sql(name=table_name, con=engine, if_exists='append', index=False)
    print('插入完毕')

    # 更新状态
    for index, row in result.iterrows():
        update(str(row['location']))
    print('更新完毕')
    time.sleep(5)


if __name__ == '__main__':
    # geojson = read_geojson('图片文件/new/YJKC01.geojson')
    # check = check_point_in_range_geojson('121.620275', '29.892255', geojson)
    # print(check)
    run()
    # 指定地图 GeoJSON 文件夹路径
    # folder_path = "/home/nbippc/geojson"
