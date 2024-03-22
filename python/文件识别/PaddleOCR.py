import os
import pytesseract
import os
from concurrent.futures import ThreadPoolExecutor
from paddleocr import PaddleOCR
import sqlalchemy
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image

# 创建数据库引擎
mysql_engine = sqlalchemy.create_engine("mssql+pymssql://sa:wlzx87811024@172.16.5.45/zhangxueyang")
ocr = PaddleOCR(use_angle_cls=True, lang="ch", det_db_thresh=0.3, det_east_score_thresh=0.8, rec_char_type='ch',
                use_gpu=False)


def extract_text_from_pdf(pdf_path):
    text = ""
    pdf_document = fitz.open(pdf_path)
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        text += page.get_text()
    pdf_document.close()
    return text


def save_text_to_database(pdf_path, extracted_text):
    # 创建数据库引擎
    mysql_engine = sqlalchemy.create_engine("mssql+pymssql://sa:wlzx87811024@172.16.5.45/zhangxueyang")

    # 创建DataFrame
    data = {'pdf_path': [pdf_path], 'text': [extracted_text]}
    df = pd.DataFrame(data)

    # 将数据保存到数据库
    df.to_sql('test_orc', mysql_engine, if_exists='append', index=False)


def convert_pdf_to_images(pdf_file):
    pdf_filename = os.path.basename(pdf_file).split('.')[0]  # 提取PDF文件名
    image_folder = os.path.join(os.path.dirname(pdf_file), pdf_filename)  # 创建文件夹路径
    print("Image folder path: " + image_folder)
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)  # 创建文件夹
        pdf_document = fitz.open(pdf_file)
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            image_list = page.get_pixmap()
            image = Image.frombytes("RGB", [image_list.width, image_list.height], image_list.samples)
            image.save(os.path.join(image_folder, f"page_{page_number + 1}.png"))  # 保存图片到指定文件夹
            print(os.path.join(image_folder, f"page_{page_number + 1}.png"))
        pdf_document.close()


def ocr_image(img_path):
    result = ocr.ocr(img_path, cls=True)
    boxes, txts, scores, sorts = [], [], [], []
    for idx, line in enumerate(result[0]):
        boxes.append(str(line[0]))  # 转换为字符串
        txts.append(str(line[1][0]))
        scores.append(str(line[1][1]))
        sorts.append(idx)  # 添加排序字段

    # 创建DataFrame
    data = {'img_path': [img_path] * len(txts), 'box': boxes, 'text': txts, 'score': scores, 'sort': sorts}
    df = pd.DataFrame(data)
    # 将数据保存到数据库
    df.to_sql('ocr_results', mysql_engine, if_exists='append', index=False, chunksize=1000)


def load_sqlserver():
    mysql_engine = sqlalchemy.create_engine("mssql+pymssql://sa:wlzx87811024@172.16.5.45/zhangxueyang?charset=GBK")
    df = pd.read_sql('select * from XXL_OU', mysql_engine)
    print(df)


def process_image(file_path):
    ocr_image(file_path)
    print('执行{}完毕'.format(os.path.basename(file_path)))


if __name__ == '__main__':
    pdf_path = "test.pdf"

    # 提取PDF文本并保存到数据库
    # extracted_text = extract_text_from_pdf(pdf_path)
    # save_text_to_database(pdf_path, extracted_text)

    # 将PDF转换为图片
    convert_pdf_to_images(pdf_path)

    # # OCR识别图片文本
    directory = r'C:\workspace\workspace\pyhton_pachong\python\文件识别\png'
    # 创建线程池
    with ThreadPoolExecutor() as executor:
        # 遍历目录下的所有文件
        for filename in os.listdir(directory):
            if filename.endswith(".png"):
                # 构建完整的文件路径
                file_path = os.path.join(directory, filename)
                # 提交任务到线程池
                executor.submit(process_image, file_path)

    # # 加载SQL Server数据
    # load_sqlserver()
