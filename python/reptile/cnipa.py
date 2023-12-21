import random
import re
import time

import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlalchemy
import uuid

# 请求头
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Length": "240",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "JSESSIONID=b7ee01b4c8cc8cd70f7ef8259055; bg47=509|Cc4TG; cookiename=value",
    "Dnt": "1",
    "Host": "dlgl.cnipa.gov.cn",
    "Origin": "http://dlgl.cnipa.gov.cn",
    "Referer": "http://dlgl.cnipa.gov.cn/",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.31"
}

headers_detail = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Length": "76",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "JSESSIONID=b7ee01b4c8cc8cd70f7ef8259055; cookiename=value; bg47=509|Cc4aV",
    "Dnt": "1",
    "Host": "dlgl.cnipa.gov.cn",
    "Origin": "http://dlgl.cnipa.gov.cn",
    "Referer": "http://dlgl.cnipa.gov.cn/",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.31"
}


def execute_title(url, data):
    list_result = []
    response = requests.post(url=url, data=data,
                             headers=headers).text  # 起始URL
    soup = BeautifulSoup(response, 'html.parser')
    # 使用soup提取网页内容
    # 例如，提取第一个表格的所有行：
    table = soup.find('table')
    trs = table.find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        result = {}
        if len(tds) > 0:
            # 继续处理第一个 td 元素
            result['agency_code'] = str(tds[0].text).replace(' ', '').replace('\n', '').replace('\t', '')
            result['agency_name'] = str(tds[1].text).replace(' ', '').replace('\n', '').replace('\t', '')
            # 获取 onclick 属性值中的关键信息
            onclick_value = tds[1].find('a').get('onclick')
            result['key_info'] = re.findall(r"\'(.+?)\'", onclick_value)[0]
            list_result.append(result)
            result['agency_status'] = str(tds[2].text).replace(' ', '').replace('\n', '').replace('\t', '')
            result['agency_type'] = str(tds[3].text).replace(' ', '').replace('\n', '').replace('\t', '')
            result['establishment_year'] = str(tds[4].text).replace(' ', '').replace('\n', '').replace('\t', '')
            result['total_patent_agents'] = str(tds[5].text).replace(' ', '').replace('\n', '').replace('\t', '')
            result['credit_rating'] = str(tds[6].text).replace(' ', '').replace('\n', '').replace('\t', '')
    print(list_result)
    # for td in range(tds):
    #     print(str(tds.text).replace(' ', '').replace('\n', '').replace('\t', ''))
    return list_result


def execute_attorney_title(url, data, header_attorney):
    list_result = []
    response = requests.post(url=url, data=data,
                             headers=header_attorney).text  # 起始URL
    soup = BeautifulSoup(response, 'html.parser')
    # 使用soup提取网页内容
    # 例如，提取第一个表格的所有行：
    table = soup.find('tbody')
    trs = table.find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        result = {}
        if len(tds) > 0:
            # 继续处理第一个 td 元素
            result['attorney_uuid'] = str(uuid.uuid4()).replace("-", "")
            result['practice_years'] = str(tds[0].text).replace(' ', '').replace('\n', '').replace('\t', '')
            result['name'] = str(tds[1].text).replace(' ', '').replace('\n', '').replace('\t', '')
            # 获取 onclick 属性值中的关键信息
            onclick_value = tds[1].find('a').get('onclick')
            result['key_info'] = re.findall(r"\'(.+?)\'", onclick_value)[0]
            list_result.append(result)
            result['qualification_number'] = str(tds[2].text).replace(' ', '').replace('\n', '').replace('\t', '')
            result['practice_registration_number'] = str(tds[3].text).replace(' ', '').replace('\n', '').replace('\t',
                                                                                                                 '')
            result['major'] = str(tds[4].text).replace(' ', '').replace('\n', '').replace('\t', '')
            result['organization_name'] = str(tds[5].text).replace(' ', '').replace('\n', '').replace('\t', '')
            result['credit_rating'] = str(tds[6].text).replace(' ', '').replace('\n', '').replace('\t', '')
    # print(list_result)
    return list_result


def test():
    response = requests.post(url='http://dlgl.cnipa.gov.cn/txnqueryAgencyOrgInfo.do',
                             data={'select-key:id': 'aTTHD62lnEQgQxhFpnyPFDZ1saidU60XeJ0KA--2VwaNoOV3Rvm7KQ!!'},
                             headers=headers_detail)
    print(response.headers)
    print(response.text)


def sent_agency_api(page):
    list_results = []
    for i in range(page, page + 100):
        count = i
        print('执行页面', i)
        data = {
            {
                "select-key:currentPage": "{}".format(i),
                "select-key:name": "",
                "select-key:qualificationcode": "",
                "select-key:certificate": "",
                "select-key:cmajor": "",
                "very-code": "2bh4",
                "select-key:sortcol": "zynum",
                "select-key:sort": "desc",
                "select-key:clmname": "name",
                "select-key:clmvalue": ""
            }
        }
        url = 'http://dlgl.cnipa.gov.cn/txnqueryAgencyOrg.do'
        try:
            a = execute_title(url, data)
            list_results.extend(a)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            break
        delay = random.uniform(0, 2)
        if i < page + 100:
            time.sleep(delay)
    print('写入数据库')
    results = pd.DataFrame(list_results)
    engin = sqlalchemy.create_engine("mysql+pymysql://sys_admin:Mysql_2023!@10.26.39.13:3306/crawling_download")
    results.to_sql("ct_cnipa_agency_main", con=engin, index=False, if_exists='append')


engin = sqlalchemy.create_engine("mysql+pymysql://sys_admin:Mysql_2023!@10.26.39.13:3306/crawling_download")


def sent_attorney_api(page, code, header_attorney):
    page_count = page
    list_results = []
    for i in range(page, 5083):
        print('执行页面', i)
        if code.__eq__(''):
            data = {
                "select-key:currentPage": "{}".format(i),
                "select-key:agencycode": "",
                "select-key:agencyname": "",
                "select-key:localoffice": "",
                "select-key:sortcol": "zynum",
                'very-code': '',
                "select-key:sort": "asc",
                "select-key:clmname": "name",
                "select-key:clmvalue": ""
            }
        else:
            data = {
                "select-key:currentPage": "{}".format(i),
                # "select-key:agencycode": "",
                # "select-key:agencyname": "",
                # "select-key:localoffice": "",
                "select-key:sortcol": "zynum",
                'very-code': code,
                "select-key:sort": "asc",
                "select-key:clmname": "name",
                # "select-key:clmvalue": ""
            }
        url = 'http://dlgl.cnipa.gov.cn/txnqueryAgent.do'
        try:
            page_count = i
            a = execute_attorney_title(url, data, header_attorney)
            list_results.extend(a)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print('写入数据库')
            results = pd.DataFrame(list_results)
            results.to_sql("ct_cnipa_attorney_main", con=engin, index=False, if_exists='append')
            write_error_page(page_count)
            code = input("请手动跳转到{}页面并填写验证码，请确认已填写验证码（回车确认）".format(page_count))
            return code
        delay = random.uniform(1.5, 3)
        if i < page + 100:
            time.sleep(delay)
    print('继续')
    if len(list_results) > 0:
        print('写入数据库')
        results = pd.DataFrame(list_results)
        results.to_sql("ct_cnipa_attorney_main", con=engin, index=False, if_exists='append')
    return page_count


def write_error_page(text):
    # 要写入的文本内容
    # 指定文件路径和文件名
    file_path = "error_page.txt"

    # 打开文件并将文本写入其中
    with open(file_path, "w") as file:
        file.write(str(text))


def read_error_page():
    # 打开文件并读取内容
    with open('error_page.txt', "r") as file:
        file_content = file.read()

    # 打印文件内容
    return file_content


if __name__ == '__main__':
    # test()
    page = read_error_page()
    cookie = input("请输入Cookie\n\r")
    header_attorney = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Length": "262",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": cookie,
        "Dnt": "1",
        "Host": "dlgl.cnipa.gov.cn",
        "Origin": "http://dlgl.cnipa.gov.cn",
        "Referer": "http://dlgl.cnipa.gov.cn/",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.31"
    }
    code = sent_attorney_api(int(page), '', header_attorney)

    print(code)
    for i in range(1000):
        page = read_error_page()
        code = sent_attorney_api(int(page), code, header_attorney)
        print('正在重新执行')
        time.sleep(1)
