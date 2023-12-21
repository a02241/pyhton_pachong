import requests
from lxml import etree
import pandas as pd
import sqlalchemy
import urllib.request
import uuid
import datetime
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import text, update
import cv2
import numpy as np

# 请求头
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Cookie': 'SERVERID=web40; _dx_captcha_cid=63357340; _dx_uzZo5y=65a81dd520fb0f07a88b2761cb5f3ddf57522cca3363197e27638ea34be22c612feb4792; _dx_FMrPY6=64a52b512EeMIyENZgsnwcjBBYtmIa6Nzq25S7I1; _dx_app_539c65e65e4a2a6db9f4696fec027609=64a52b512EeMIyENZgsnwcjBBYtmIa6Nzq25S7I1; Hm_lvt_0d80c28f5b9b99aec47d7708b46b37e7=1688546212; _dx_captcha_vid=ECC47CE8BD847DE10E3E680D522667F11C1900CFE8C805222A45877BE2AD21B566AB378C52548D178CDB64283BB81C6ADDE204F315B844D2FAC53FB9B97ABC5F28AFA2CC21DE66FC8795714F5D5F980D; Hm_lpvt_0d80c28f5b9b99aec47d7708b46b37e7=1688972981',
    'Host': 'www.51chuli.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67'
}


def execute_title(url):
    list_result = []
    response = requests.get(url=url, headers=headers).text  # 起始URL
    fen1 = etree.HTML(response)
    dl = fen1.xpath(
        '/html/body/div[2]/div[2]/div[1]/div[1]/div/dl')
    for dd in dl:
        result = {}
        result['title_uuid'] = str(uuid.uuid4()).replace("-", "")
        result['title_text'] = ''
        result['title_href'] = ''
        result['title_describe'] = ''
        result['title_price'] = ''
        result['title_condition'] = ''
        result['title_place'] = ''
        result['title_time'] = ''
        result['title_img'] = ''
        result['title_img_name'] = ''
        result['title_img_address'] = ''
        result['title_status'] = 0
        result['title_create_time'] = datetime.datetime.now()
        a = dd.xpath('./dd/h5/span/a')
        if a:
            link_text = a[0].text
            link_href = a[0].get('href')
            result['title_text'] = link_text
            result['title_href'] = link_href
        else:
            print('Link element not found.')
        result['title_describe'] = dd.xpath('./dd/p[1]/span[1]')[0].text
        result['title_price'] = dd.xpath('./dd/p[1]/b[1]')[0].text
        result['title_condition'] = dd.xpath('./dd/div[1]/span')[0].text
        if dd.xpath('./dd/p[2]/span/a[2]'):
            result['title_place'] = dd.xpath('./dd/p[2]/span/a[1]')[0].text + '-' + dd.xpath('./dd/p[2]/span/a[2]')[
                0].text
        else:
            result['title_place'] = dd.xpath('./dd/p[2]/span/a[1]')[0].text
        result['title_time'] = str(dd.xpath('./dd/p[2]/span/text()[1]')[0]).replace(' ', '').replace(' ', '')
        if str(result['title_time']).replace(' ', '').__eq__('-'):
            result['title_time'] = str(dd.xpath('./dd/p[2]/span/text()[2]')[0]).replace(' ', '').replace(' ', '')
        result['title_img'] = dd.xpath('./dt/a/img')[0].get('src')
        img_name = result['title_img'].split("/")[-1]
        result['title_img_name'] = img_name
        save_path = "E:/img/title/" + img_name
        result['title_img_address'] = save_path
        # urllib.request.urlretrieve(result['title_img'], save_path)
        print(result['title_img'])
        list_result.append(result)
    return list_result


def search_title():
    url = 'https://www.51chuli.com/zhusuji/'
    list_results = []
    list_results.extend(execute_title(url))
    for i in range(2, 12):
        print('执行页面', i)
        url = 'https://www.51chuli.com/zhusuji/p' + str(i) + '/'
        a = execute_title(url)
        list_results.extend(a)
    for item in list_results:
        print(item)
    results = pd.DataFrame(list_results)
    engin = sqlalchemy.create_engine("mssql+pymssql://sa:wlzx87811024@172.16.5.45/NBSTIMachine")
    results.to_sql("clw_title", con=engin, index=False, if_exists='append')
    print('finish')


# 爬取详细信息
def execute_detail():
    engin = sqlalchemy.create_engine("mssql+pymssql://sa:wlzx87811024@172.16.5.45/NBSTIMachine")
    query = "SELECT title_uuid,title_href FROM clw_title WHERE title_status = 0"
    result = engin.execute(query)
    print(result)
    # 遍历结果
    for row in result:
        list_detail = []
        list_imgs = []
        detail = {}
        print(row['title_href'])
        response = requests.get(url=row['title_href'], headers=headers).text  # 起始URL
        fen1 = etree.HTML(response)
        # /html/body/div[2]/div[2]/div[1]/div[1]/h1
        detail['detail_uuid'] = str(uuid.uuid4()).replace("-", "")
        detail['title_uuid'] = row['title_uuid']
        detail['detail_title'] = ''
        detail['detail_title'] = fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[1]/h1')[0].text
        detail['detail_no'] = ''
        detail['detail_no'] = fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[1]/div/span[1]/label')[0].text
        # 发布时间
        detail['detail_release_time'] = ''
        detail['detail_release_time'] = fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[1]/div/span[2]/label')[0].text
        # 浏览
        detail['detail_browse'] = ''
        detail['detail_browse'] = fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[1]/div/span[3]/label')[0].text
        # 价格
        detail['detail_price'] = ''
        detail['detail_price'] = fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/p[1]/span[1]/b')[0].text
        # 价格
        detail['detail_condition'] = ''
        detail['detail_condition'] = fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/p[1]/span[2]/label')[
            0].text
        # # 所在地
        # detail['detail_place'] = ''
        # place = fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/p[2]/span[1]/a[1]')
        # if place:
        #     print(place[0].text)
        #     if place[0].text is not None and place[0].text is not 'None':
        #         detail['detail_place'] = \
        #             fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/p[2]/span[1]/a[1]')[
        #                 0].text + '-' + \
        #             fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/p[2]/span[1]/a[2]')[
        #                 0].text
        #     else:
        #         detail['place'] = fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/p[2]/span[1]/a[2]')[
        #             0].text
        # 交易地点
        detail['detail_transaction_place'] = ''
        detail['detail_transaction_place'] = \
            fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/p[2]/span[2]/label')[
                0].text
        # 联系人
        detail['detail_contacts'] = ''
        detail['detail_contacts'] = \
            fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/p[3]/span')[
                0].text
        # 手机
        detail['detail_phone'] = ''
        phone = fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/p[4]/b')
        if phone:
            detail['detail_phone'] = phone[0].text
        else:
            detail['detail_phone'] = fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/p[4]/img')[0].get('src')
        # QQ
        detail['detail_qq'] = ''
        qq = fen1.xpath('//*[@class="qqnum"]/a')
        if qq:
            detail['detail_qq'] = qq[0].text
        print(detail['detail_qq'])
        # 公司
        detail['detail_company'] = ''
        company = fen1.xpath('//*[@class="company"]/span')
        if company:
            detail['detail_company'] = company[0].text
        print(detail['detail_company'])
        # 归属地
        detail['detail_phone_place'] = ''
        detail['detail_phone_place'] = fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[2]/div[2]/p[4]/text()[2]')[0]

        # 描述//*[@id="img_ul2"]/ul/li[1]/img
        detail['detail_description'] = ''
        description = fen1.xpath('/html/body/div[2]/div[2]/div[1]/div[3]/p')
        description_str = ''
        for p in description:
            description_str = description_str + '\n' + p.text
        detail['detail_description'] = description_str
        img = fen1.xpath('//*[@id="img_ul2"]/ul/li')
        if img:
            for li in img:
                imgs = {}
                imgs['uuid'] = str(uuid.uuid4()).replace("-", "")
                imgs['title_uuid'] = detail['detail_uuid']
                imgs['detail_img'] = li.xpath('./img')[0].get('src')
                detail_img_name = imgs['detail_img'].split("/")[-1]
                imgs['detail_img_address'] = li.xpath('./img')[0].get('src')
                imgs['detail_img_name'] = detail_img_name
                save_path = "E:/img/detail/" + detail_img_name
                imgs['detail_img_address'] = save_path
                imgs['detail_img_status'] = save_path
                list_imgs.append(imgs)

        list_detail.append(detail)
        # 插入
        results_detail = pd.DataFrame(list_detail)
        results_detail.to_sql("clw_detail", con=engin, index=False, if_exists='append')
        #
        results_img = pd.DataFrame(list_imgs)
        results_img.to_sql("clw_detail_img", con=engin, index=False, if_exists='append')
        #
        # 定义更新语句
        sql = "update clw_title set title_status=1 where title_uuid ='{title_uuid}'".format(
            title_uuid=row['title_uuid'])
        engin.execute(sql)

    # for item in list_detail:
    #     print(item)

    # 关闭连接
    result.close()

    print('finish')


# 下载图片
def excute_img():
    engin = sqlalchemy.create_engine("mssql+pymssql://sa:wlzx87811024@172.16.5.45/NBSTIMachine")
    query = "SELECT top 5000 uuid,detail_img,detail_img_address FROM clw_detail_img WHERE detail_img_status = 0"
    result = engin.execute(query)
    count = 0
    for row in result:
        count = count + 1
        print('执行第' + str(count) + '条:' + row['detail_img'])
        urllib.request.urlretrieve(row['detail_img'], row['detail_img_address'])
        sql = "update clw_detail_img set detail_img_status=1 where uuid ='{uuid}'".format(
            uuid=row['uuid'])
        engin.execute(sql)
    result.close()


# 截取图片并保存
def crop_image(image_path):
    # 读取原始图片
    image = cv2.imread(image_path)

    # 获取图片的高度和宽度
    height, width = image.shape[:2]

    # 截取图片的下面六分之一位置
    cropped_image = image[:int(height * 5 / 6), :]

    return cropped_image


# 截取突破处理
def execute_crop_img():
    engin = sqlalchemy.create_engine("mssql+pymssql://sa:wlzx87811024@172.16.5.45/NBSTIMachine")
    query = "SELECT detail_img_address FROM clw_detail_img"
    result = engin.execute(query)
    count = 0
    for row in result:
        count = count + 1
        print('执行第' + str(count) + '条:' + row['detail_img_address'])
        # 替换为你的原始图片路径
        image_path = row['detail_img_address']

        # 截取图片
        cropped_image = crop_image(image_path)

        # 保存截取后的图片
        cv2.imwrite(str(row['detail_img_address']).replace('detail', 'detail_crop'), cropped_image)
    result.close()

    print('finish')


if __name__ == '__main__':
    # search_title()
    execute_detail()
    # excute_img()
    # execute_crop_img()
