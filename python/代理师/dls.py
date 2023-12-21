import requests
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
import re

cookie = 'cookiename=value; bg47=509|CkDaD; JSESSIONID=bcd1525eef0ad8cc5933143c4641; SSOTOKEN=beacon!0373577DB5545268C3963473659D6C03907033731C7524C62A208C51A2E6DA332936D938B44173CC30C3DAEB22BCEFDD337460F743099ED717A6A2FC98C4915A; menu-path=/tjcx/tjcx/dlr'


# 获取代理师list数据
def search_branch_dls_list(index):
    url = 'http://dlgl.cnipa.gov.cn/txn20a1010.ajax?inner-flag:open-type=new-window&inner-flag:freeze-stamp=1702875337603&inner-flag:back-flag=true&freeze-next-page=npage&inner-flag:grid-name=20a1010/record&inner-flag:page-name=/app/tjcx/dlr/query-dfj_cxtj_dlrxxcx_list.jsp&inner-flag:file-type=ajax-grid&attribute-node:record_sort-column=&attribute-node:record_page-row=10&attribute-node:record_start-row={row}&attribute-node:record_record-number=1767&path=/tjcx/tjcx/dlr&cmd=统计查询/专利代理师查询&charset-encoding=UTF-8' \
        .format(row=(index * 50 + 1))
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN',
        'Connection': 'Keep-Alive',
        'Cookie': cookie,
        'Host': 'dlgl.cnipa.gov.cn',
        'Referer': 'http://dlgl.cnipa.gov.cn/txn20a1010.do',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    res = requests.post(url=url, headers=headers)
    # print(res)
    res.encoding = 'utf-8'
    return res.text


# 分支结构list
def search_branch_fzjg_list(index):
    url = 'http://dlgl.cnipa.gov.cn/txn20a1025.ajax?inner-flag:open-type=new-window&inner-flag:freeze-stamp=1702885403649&inner-flag:back-flag=true&freeze-next-page=npage&inner-flag:grid-name=20a1025/record&inner-flag:page-name=/app/tjcx/dlr/query-dfj_cxtj_branch_list.jsp&inner-flag:file-type=ajax-grid&attribute-node:record_sort-column=&attribute-node:record_page-row=600&attribute-node:record_start-row={row}&attribute-node:record_record-number=578&path=/tjcx/tjcx/dlr&cmd=统计查询/分支机构查询&charset-encoding=UTF-8' \
        .format(row=(index * 50 + 1))
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN',
        'Connection': 'Keep-Alive',
        'Cookie': cookie,
        'Host': 'dlgl.cnipa.gov.cn',
        'Referer': 'http://dlgl.cnipa.gov.cn/txn20a1025.do',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    res = requests.post(url=url, headers=headers)
    # print(res)
    res.encoding = 'utf-8'
    return res.text


# 获取代理师页面详情数据
def search_branch_dls_detail(id, qualificationcode):
    url = 'http://dlgl.cnipa.gov.cn/txn20a1050.do?select-key:id={id}&record:cnkeyword=åºæµ&select-key:qualificationcode={qualificationcode}&select-key:zgz=1&inner-flag:open-type=window&inner-flag:flowno=1702878917232&inner-flag:pre-page=/txn20a1010.do' \
        .format(id=id, qualificationcode=qualificationcode)
    # url = 'http://dlgl.cnipa.gov.cn/txn20a1050.do?select-key:id={id}'.format(
    #     id=id)
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN',
        'Connection': 'Keep-Alive',
        'Cookie': cookie,
        'Host': 'dlgl.cnipa.gov.cn',
        'Referer': 'http://dlgl.cnipa.gov.cn/txn20a1050.do',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    res = requests.get(url=url, headers=headers)
    res.encoding = 'utf-8'
    return res.text


def search_branch(id, agencycode):
    url = 'http://dlgl.cnipa.gov.cn/txn20a1070.do?' \
          'select-key:id={id}&select-key:agencycode={agencycode}' \
          '&query-key:backtype=dfj&query-key:select-key:njid=&query-key:agencyname=' \
          '&query-key:agencycode=&query-key:economictype=&query-key:agencytype=&' \
          'query-key:defenseflag=&query-key:createdatestart=&query-key:createdateend=&inner-flag:open-type=window&inner-flag:flowno=1702868953572&inner-flag:pre-page=/txn20a1011.do'.format(
        id=id, agencycode=agencycode)
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN',
        'Connection': 'Keep-Alive',
        'Cookie': cookie,
        'Host': 'dlgl.cnipa.gov.cn',
        'Referer': 'http://dlgl.cnipa.gov.cn/txn20a1011.do',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    res = requests.get(url=url, headers=headers)
    res.encoding = 'utf-8'
    return res.text


# 机构详情数据
def load_jg_detail(id, agencycode):
    text = search_branch(id, agencycode)
    soup = BeautifulSoup(text, 'html.parser')
    # 查找机构名称
    agencyname = soup.find('span', id='span_record:agencyname').text
    # 查找机构代码
    agencycode = soup.find('span', id='span_record:agencycode').text
    # 查找负责人
    principal = soup.find('span', id='span_record:principal').text
    # 合伙人/股东/设立人：
    parter = soup.find('span', id='span_record:parter').text
    # 双证人员：
    doublecert = soup.find('span', id='span_record:parter').text
    # 查找联系电话
    phone = soup.find('span', id='span_record:phone').text
    # 查找传真
    fax = soup.find('span', id='span_record:fax').text
    # 查找网址
    agencyurl = soup.find('span', id='span_record:agencyurl').text
    # 查找邮箱
    email = soup.find('span', id='span_record:email').text
    # 查找邮编
    postcode = soup.find('span', id='span_record:postcode').text
    # 查找机构状态
    status = soup.find('span', id='span_record:status').text
    # 代理师
    agent = soup.find('span', id='span_record:agent').text
    # 地址
    address = soup.find('span', id='span_record:address').text
    # 申请机构执业许可的办理方式
    isgzcn = soup.find('span', id='span_record:isgzcn').text
    # 统一社会信用代码
    tyshxycode = soup.find('span', id='span_record:tyshxycode').text
    data = {
        'agencyname': [agencyname],
        'agencycode': [agencycode],
        'principal': [principal],
        'parter': [parter],
        'doublecert': [doublecert],
        'phone': [phone],
        'fax': [fax],
        'agencyurl': [agencyurl],
        'email': [email],
        'postcode': [postcode],
        'status': [status],
        'agent': [agent],
        'address': [address],
        'isgzcn': [isgzcn],
        'tyshxycode': [tyshxycode]
    }
    df = pd.DataFrame(data)

    insert_mysql(df, 'ct_dljg')
    init_script(soup, agencyname)


# 解析script
def init_script(soup, agencyName):
    # 查找所有的script标签
    scripts = soup.find_all('script')
    # 输出所有script标签的内容
    tbody_content = ''
    for script in scripts:
        script = script.text.replace('\n', '')
        # 使用正则表达式匹配出tbody的内容
        tbody_pattern = re.compile(r"var rs=(.*?)];", re.DOTALL)
        match = re.search(tbody_pattern, script)
        if match:
            tbody_content = match.group(1)
    if 'null' not in tbody_content:
        tbody_content = tbody_content + "]"
        content = eval(tbody_content)
        content = content[1:]
        df = pd.DataFrame(content,
                          columns=['@key', '@rowid', 'branchname', 'branchcode', 'principal', 'agent', 'phone',
                                   'address',
                                   'id'])
        df['agencyname'] = agencyName
        # 按照期望的顺序重新定义列
        df = df[
            ['agencyname', '@key', '@rowid', 'branchname', 'branchcode', 'principal', 'agent', 'phone', 'address',
             'id']]
        insert_mysql(df, 'ct_dljg_fz')


def insert_mysql(results, table):
    mysql_engine = create_engine("mysql+pymysql://sys_admin:Mysql_2023!@10.26.39.12/public_interface")
    # 将结果数据存储到 MySQL 数据库中
    results.to_sql(table, con=mysql_engine, index=False, if_exists='append')


def load_txt():
    # 从txt文件中读取数据到列表
    data = []
    # 读取txt文件
    with open('test.txt', 'r', encoding='utf-8') as file:
        content = file.read()
    # 将字符串转换为列表
    info_list = eval(content)
    df = pd.DataFrame(info_list, columns=['@key', 'agencyname', 'agencycode', 'postcode', 'email', 'principal', 'phone',
                                          'createdate', 'address', 'zynum'])
    df['status'] = '0'
    df = df.astype(str)
    insert_mysql(df, 'ct_dljg_list')


# 机构数据入库
def init_dljg():
    mysql_engine = create_engine("mysql+pymysql://sys_admin:Mysql_2023!@10.26.39.12/public_interface")
    df = pd.read_sql('select * from public_interface.ct_dljg_list where status = 0', mysql_engine)
    # 连接到数据库
    conn = mysql_engine.connect()
    # 编写要执行的 Update 语句
    update_query = "update  public_interface.ct_dljg_list set status = 1 where `@key` = '{}'"
    # 执行 Update 语句
    # 关闭数据库连接
    for index, row in df.iterrows():
        print(row['agencyname'])
        load_jg_detail(row['@key'], row['agencyname'])
        conn.execute(update_query.format(row['@key']))
    conn.close()


# 获取所有代理师数据
def load_dls_list():
    # 1757
    for i in range(36):
        print(i + 1)
        cdata = search_branch_dls_list(i + 1)
        soup = BeautifulSoup(cdata, 'html.parser')
        # 查找所有的script标签
        scripts = soup.find_all('record')
        # 输出所有script标签的内容
        tbody_content = scripts[0].text
        content = eval(tbody_content)
        content = content[1:]
        df = pd.DataFrame(content,
                          columns=['@key', 'name', 'sex', 'birthdate', 'certificate', 'qualificationcode', 'agencycode',
                                   'cmajor', 'id', 'localoffice', 'cnkeyword'])
        df = df.astype(str)
        insert_mysql(df, 'ct_dls_list')


# 解析代理师数据
def load_dls():
    mysql_engine = create_engine("mysql+pymysql://sys_admin:Mysql_2023!@10.26.39.12/public_interface")
    df = pd.read_sql('select * from public_interface.ct_dls_list where status = 0 ', mysql_engine)
    # 连接到数据库
    conn = mysql_engine.connect()
    # 编写要执行的 Update 语句
    update_query = "update  public_interface.ct_dls_list set status = 1 where `@key` = '{}'"
    for index, row in df.iterrows():
        print(row['name'])
        html_text = search_branch_dls_detail(row['@key'], row['qualificationcode'])
        soup = BeautifulSoup(html_text, 'html.parser')
        # 查找机构名称
        data = {
            'name': [soup.find('span', id='span_record:name').text],
            'sex': [soup.find('span', id='span_record:sex').text],
            'birthdate': [soup.find('span', id='span_record:birthdate').text],
            'nationality': [soup.find('span', id='span_record:nationality').text],
            'cardtype': [soup.find('span', id='span_record:cardtype').text],
            'no': [soup.find('span', id='span_record:no').text],
            'education': [soup.find('span', id='span_record:education').text],
            'cmajor': [soup.find('span', id='span_record:cmajor').text],
            'ispartner': [soup.find('span', id='span_record:ispartner').text],
            'certificate': [soup.find('span', id='span_record:certificate').text],
            'qualificationcode': [soup.find('span', id='span_record:qualificationcode').text],
            'foreignlanuage': [soup.find('span', id='span_record:foreignlanuage').text],
            'qualificationtype': [soup.find('span', id='span_record:qualificationtype').text],
            'otherqualification': [soup.find('span', id='span_record:otherqualification').text],
            'qualifydate': [soup.find('span', id='span_record:qualifydate').text],
            'firstbusinessdate': [soup.find('span', id='span_record:firstbusinessdate').text],
            'phone': [soup.find('span', id='span_record:phone').text],
            'postcode': [soup.find('span', id='span_record:postcode').text],
            'houseraddress': [soup.find('span', id='span_record:houseraddress').text],
            'filesplace': [soup.find('span', id='span_record:filesplace').text],
            'filesunit': [soup.find('span', id='span_record:filesunit').text],
            'filesunitlinkman': [soup.find('span', id='span_record:filesunitlinkman').text],
            'filesunitphone': [soup.find('span', id='span_record:filesunitphone').text],
            'isretire': [soup.find('span', id='span_record:isretire').text],
            'retiredate': [soup.find('span', id='span_record:retiredate').text],
            'retireunit': [soup.find('span', id='span_record:retireunit').text],
            'agencyname': [soup.find('span', id='span_record:agencyname').text],
            'agencycode': [soup.find('span', id='span_record:agencycode').text],
            'agencypostcode': [soup.find('span', id='span_record:agencypostcode').text],
            'agencyaddress': [soup.find('span', id='span_record:agencyaddress').text],
            'agencyphone': [soup.find('span', id='span_record:agencyphone').text],
            'agenttime': [soup.find('span', id='span_record:agenttime').text],
            'isdlrcy': [soup.find('span', id='span_record:isdlrcy').text]
        }

        df = pd.DataFrame(data)
        df = df.astype(str)
        # 插入代理师信息
        insert_mysql(df, 'ct_dls_detail')
        # 查找所有的script标签
        scripts = soup.find_all('script')
        # 输出所有script标签的内容
        education_content = ''
        work_content = ''
        zybalist_content = ''
        for script in scripts:
            script = script.text.replace('\n', '')
            # 使用正则表达式匹配出tbody的内容
            tbody_pattern = re.compile(r"var rs=(.*?)];", re.DOTALL)
            match = re.search(tbody_pattern, script)
            if match:
                if 'studystartdate' in match.group(1):
                    education_content = match.group(1)
                if 'workid' in match.group(1):
                    work_content = match.group(1)
                if 'zybaid' in match.group(1):
                    zybalist_content = match.group(1)
        if 'null' not in education_content:
            tbody_content = education_content + "]"
            content = eval(tbody_content)
            content = content[1:]
            education = pd.DataFrame(content,
                                     columns=['@key', 'studystartdate', 'studyenddate', 'studyunit', 'degree', 'eduid',
                                              'id'])
            education['person_id'] = row['@key']
            # 按照期望的顺序重新定义列
            education = education[
                ['person_id', '@key', 'studystartdate', 'studyenddate', 'studyunit', 'degree', 'eduid', 'id']]
            education = education.astype(str)
            # 插入学历信息
            insert_mysql(education, 'ct_dls_education')
        if 'null' not in work_content:
            tbody_content = work_content + "]"
            content = eval(tbody_content)
            content = content[1:]
            df_work = pd.DataFrame(content,
                                   columns=['@key', 'workstartdate', 'workenddate', 'workunit', 'workduty', 'workid',
                                            'id'])
            df_work['person_id'] = row['@key']
            df_work = df_work[
                ['person_id', '@key', 'workstartdate', 'workenddate', 'workunit', 'workduty', 'workid', 'id']]
            df_work = df_work.astype(str)
            # 插入工作信息
            insert_mysql(df_work, 'ct_dls_work')
        if 'null' not in zybalist_content:
            tbody_content = zybalist_content + "]"
            content = eval(tbody_content)
            content = content[1:]
            zybalist = pd.DataFrame(content,
                                    columns=['@key', 'workstartdate', 'workenddate', 'workunit', 'workduty', 'zybaid'])
            zybalist['person_id'] = row['@key']
            zybalist = zybalist[
                ['person_id', '@key', 'workstartdate', 'workenddate', 'workunit', 'workduty', 'zybaid']]
            zybalist = zybalist.astype(str)
            # 插入职业经历
            insert_mysql(zybalist, 'ct_dls_zybalist')
        conn.execute(update_query.format(row['@key']))
    conn.close()


# 所有分支机构列表信息
def load_fzjg():
    for i in range(1):
        print(i + 1)
        cdata = search_branch_fzjg_list(i + 1)
        soup = BeautifulSoup(cdata, 'html.parser')
        # 查找所有的script标签
        scripts = soup.find_all('record')
        # 输出所有script标签的内容
        tbody_content = scripts[0].text
        content = eval(tbody_content)
        content = content[1:]
        df = pd.DataFrame(content,
                          columns=['@key', 'agencycode', 'branchname', 'branchcode', 'principal', 'localoffice',
                                   'createdate', 'postcode', 'address', 'phone', 'agent', 'status', 'id'])
        df = df.astype(str)
        insert_mysql(df, 'ct_fzjg_list')


if __name__ == '__main__':
    # 机构数据入库
    # init_dljg()
    # 爬取所有代理师list数据入库
    # load_dls_list()
    # 爬取代理师详情数据
    # load_dls()
    # 分支机构列表信息
    load_fzjg()