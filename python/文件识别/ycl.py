import time
import pytesseract
from PIL import Image

import easyocr
import ddddocr


def ocr_easyocr(img):
    reader = easyocr.Reader(['ch_sim'], gpu=False)
    result = reader.readtext(img)
    print(result)


def ddddd_ocr():
    ocr = ddddocr.DdddOcr()
    # 请将下面路径改为用户需要识别图片的路径
    with open("C:\workspace\workspace\pyhton_pachong\python\文件识别\png\page_44.png", 'rb') as f:
        img_bytes = f.read()
    res = ocr.classification(img_bytes)
    print(res)


if __name__ == '__main__':
    start_time = time.time()
    # test = ocr_easyocr('C:\workspace\workspace\pyhton_pachong\python\文件识别\png\page_1.png')

    text = pytesseract.image_to_string(Image.open("C:\workspace\workspace\pyhton_pachong\python\文件识别\png\page_8.png"), lang='chi_sim')
    print(text)
    # ddddd_ocr()
    end_time = time.time()
    print('\n ==== OCR cost time: {} ===='.format(end_time - start_time))
