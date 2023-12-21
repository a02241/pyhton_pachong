import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import sqlalchemy
import threading


def get_detail(driver, title_name):
    driver.get(file_path + r'/{name}.htm#{name}'.format(name=title_name))
    start = str(str(title_name)[0:1])
    lists = []
    details = driver.find_elements(By.CSS_SELECTOR, "[role='row']")
    print('读取{name}中'.format(name=title_name))
    for row in details:
        name = row.find_elements(By.CLASS_NAME, 'symbol')
        aa = row.find_elements(By.CLASS_NAME, "l1")
        # if len(aa) > 0:
        #     ag = aa[0].text
        #     if ag.__contains__('(trans'):
        #         continue
        if len(name) > 0:
            lists.append(name[0].text)
        if len(aa) > 0:
            tag = aa[0].text
            lists.append(tag)
        lists.append('<--------->')
    print('读取{name}完毕,数据整合中'.format(name=title_name))
    lists2 = []
    list_title = []
    list_result = []
    result_title = {}
    result_title['description'] = ''
    result_title['version'] = ''
    list_title.append(0)
    for i in range(len(lists)):
        detail = lists[i]
        if str(detail).__contains__('<--------->') and i < len(lists) - 1 and len(
                lists[i + 1]) < 13 and str(lists[i + 1]).__contains__(start) and len(lists[i + 1]) > 5 and str(
            lists[i + 1]).__contains__('/'):
            lists2.append(i)
        elif str(detail).__contains__('<--------->'):
            list_title.append(i)
    lists2.append(len(lists) - 1)
    count = 1
    # 头
    # 筛选头部数据截取
    list_check = [one for one in list_title if one > lists2[0]]
    list_check = list_check[:-1]
    list_title = [one for one in list_title if one < lists2[0]]
    list_title.append(list_title[len(list_title) - 1] + 3)
    for i in range(len(list_title)):
        if i < len(list_title) - 1:
            new_list = lists[list_title[i] + 1:list_title[i + 1]]
            # print(new_list)
            # print(len(new_list))
            if i == 0:
                result_title['codeId'] = start
                result_title['detail'] = new_list[0]
            if len(new_list) == 1:
                if str(new_list[0]).startswith('Note'):
                    result_title['version'] = new_list[0][9:16]
                result_title['description'] = result_title['description'] + new_list[0]
            if len(new_list) == 2:
                result_title['sort'] = count
                result_title['tier'] = count
                result_title['parentId'] = str(result_title['codeId'])[:count]
                count = count + 1
                list_result.append(result_title)
                result_title = {}
                result_title['description'] = ''
                result_title['codeId'] = new_list[0]
                result_title['detail'] = new_list[1]
            if i == len(list_title) - 2:
                result_title['sort'] = count
                result_title['tier'] = count
                result_title['parentId'] = str(result_title['codeId'])[:count]
                count = count + 1
                list_result.append(result_title)
                result_title = {}
    # 详情
    for i in range(len(lists2)):
        if i < len(lists2) - 1:
            result = {}
            new_list = lists[lists2[i] + 1:lists2[i + 1]]
            result['codeId'] = str(new_list[0]).replace(' ', '')
            if str(new_list[1]).__contains__('(transferred'):
                result['detail'] = str(new_list[1]).replace('•\n', '')
            else:
                result['detail'] = str(new_list[1][:-10]).replace('•\n', '')
            result['tier'] = new_list[1].count("•") + 4
            if '(transferred' not in str(new_list[1]):
                result['version'] = None
            else:
                result['version'] = new_list[1][-8:-1]
            result['sort'] = count
            if lists2[i] > 2 and lists2[i] - 2 in list_check:
                result['description'] = lists[lists2[i] - 1:lists2[i]]
            else:
                result['description'] = None
            count = count + 1
            if i == 0:
                result['parentId'] = None
            for k in range(len(list_result) - 1, -1, -1):
                if int(result['tier']) > 3 and int(list_result[k]['tier']) == int(result['tier']) - 1:
                    result['parentId'] = list_result[k]['codeId']
                    break
                elif int(result['tier']) == 3:
                    result['parentId'] = str(title_name)[:3]
            list_result.append(result)
    results = pd.DataFrame(list_result)
    for row in results.itertuples():
        print(str(getattr(row, 'tier')) + str(':::') + str(
            getattr(row, 'version')) + str(':::') + str(getattr(row, 'sort')) + str(
            '~~~~') + str(getattr(row, 'codeId')) + str('--') + str(
            getattr(row, 'parentId')) + str('~~~~') + str(
            getattr(row, 'detail')) + str('~~~~') + str(
            getattr(row, 'version')) + str('~~~~') + str(getattr(row, 'description')))
    return driver, results


def test():
    chromedriver_path = r"./msedgedriver.exe"
    driver = webdriver.Edge(executable_path=chromedriver_path)
    driver.get(file_path + r'/index.htm')
    details = driver.find_elements(By.CSS_SELECTOR, "[role='row']")
    list_main_head = []
    list_detail_head = []
    list_details = []
    for row in details:
        name = row.find_elements(By.CLASS_NAME, 'symbol')
        if len(name) > 0:
            list_main_head.append(name[0].text)
    for main_detail in list_main_head:
        driver.get(file_path + r'/{name}.htm'.format(name=main_detail))
        details = driver.find_elements(By.CSS_SELECTOR, "[role='row']")
        for row in details:
            name = row.find_elements(By.CLASS_NAME, 'symbol')
            if len(name) > 0:
                if len(name[0].text) > 1:
                    list_detail_head.append(name[0].text)
    for detail_head in list_detail_head:
        driver.get(file_path + r'/{name}.htm'.format(name=detail_head))
        details = driver.find_elements(By.CSS_SELECTOR, "[role='row']")
        for row in details:
            name = row.find_elements(By.CLASS_NAME, 'symbol')
            if len(name) > 0:
                if len(name[0].text) > 3:
                    list_details.append(name[0].text)
    return driver, list_details


def dxc(engin, driver, list_details):
    for detail in list_details:
        print(detail)
        driver, results = get_detail(driver, detail)
        results.to_sql(data_name, con=engin, index=False, if_exists='append')


file_path = 'E:\package/2023/'
data_name = 'CT_IPC_2023'

if __name__ == '__main__':
    # chromedriver_path = r"./msedgedriver.exe"
    # driver = webdriver.Edge(executable_path=chromedriver_path)
    # get_detail(driver, 'A01B')

    driver, list_details = test()
    engin = sqlalchemy.create_engine("mssql+pymssql://sa:wlzx87811024@172.16.5.45/WebCollection")
    for detail in list_details:
        print(detail)
        driver, results = get_detail(driver, detail)
        results.to_sql(data_name, con=engin, index=False, if_exists='append')

    # threads = []
    # for x in range(3):
    #     t = threading.Thread(target=dxc, args=(engin, driver, list_details,))
    #     # 把多线程的实例追加入列表，要启动几个线程就追加几个实例
    #     threads.append(t)
    # for thr in threads:
    #     # 把列表中的实例遍历出来后，调用start()方法以线程启动运行
    #     thr.start()
    # for thr in threads:
    #     """
    #     isAlive()方法可以返回True或False，用来判断是否还有没有运行结束
    #     的线程。如果有的话就让主线程等待线程结束之后最后再结束。
    #     """
    #     if thr.isAlive():
    #         thr.join()
    driver.quit()
    print('finish')
