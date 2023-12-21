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
    "Content-Length": "78459",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "Hm_lvt_1067a6b069a094a18ed1330087b6bbd1=1697612846; searchcol=%u5730%u5740; JSESSIONID=19E0E2DFC910B74CCE41F4434AE8D11E; Hm_lpvt_1067a6b069a094a18ed1330087b6bbd1=1697618630",
    "Dnt": "1",
    "Host": "chinaip.cnipa.gov.cn",
    "Origin": "http://chinaip.cnipa.gov.cn",
    "Referer": "http://chinaip.cnipa.gov.cn/search!doOverviewSearch.action?type=navdb&db=all&id=3558_3667",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60"
}


def run_sj(data):
    response = requests.post(url="http://chinaip.cnipa.gov.cn/search!doOverviewSearch.action", data=data,
                             headers=headers).text  # 起始URL
    soup = BeautifulSoup(response, 'html.parser')
    g_item = soup.select('div.g_item')
    list_result = []
    for item in g_item:
        result = {}
        tit = item.select('div.g_tit')
        lines = str(tit[0].text.strip()).splitlines()
        result['bt'] = lines[0]
        result['lx'] = lines[1]
        result['sfyx'] = lines[2]
        result['sqh'] = ''
        result['sqr'] = ''
        result['gkh'] = ''
        result['gkr'] = ''
        result['trsq'] = ''
        result['faysqh'] = ''
        result['zlqr'] = ''
        result['flh'] = ''
        result['yxq'] = ''
        result['zy'] = ''

        # 获取申请号
        sqh = item.select_one('a[href*=viewDetail]').text.strip()
        result['sqh'] = str(sqh)
        # 获取申请日
        sqr = item.select_one('span:contains("申请日：")').next_sibling.strip()
        result['sqr'] = str(sqr)
        # 获取公开号
        gkh = item.select_one('span:contains("公开(公告)号：")').next_sibling
        if gkh is not None:
            result['gkh'] = str(gkh.strip())
        # 获取公开日
        gkr = item.select_one('span:contains("公开(公告)日：")').next_sibling
        if gkr is not None:
            result['gkr'] = str(gkr.strip())
        # 同日申请
        trsq = item.select_one('span:contains("同日申请：")').next_sibling
        if trsq is not None:
            result['trsq'] = str(trsq.strip())
        # 分案原申请号
        faysqh = item.select_one('span:contains("分案原申请号：")').next_sibling
        if faysqh is not None:
            result['faysqh'] = str(faysqh.strip())
        # 获取申请(专利权)人
        zlqr = item.select_one('td[colspan="2"] span:contains("申请(专利权)人：")').next_sibling
        if zlqr is not None:
            result['zlqr'] = str(zlqr.strip())
        # 获取分类号
        flh = item.select_one('td[colspan="2"] span:contains("分类号：")').next_sibling
        if flh is not None:
            result['flh'] = str(flh.strip())
        # 获取优先权
        yxq = item.select_one('td[colspan="2"] span:contains("优先权：")').next_sibling
        if yxq is not None:
            result['yxq'] = str(yxq.strip())
        # 优先权 = item.select_one('td[colspan="2"] span:contains("优先权：")').next_sibling.strip()
        # 获取摘要
        zy = item.select_one('span[name="patab"]').text.strip()
        result['zy'] = str(zy)
        list_result.append(result)
        print(result)
    results = pd.DataFrame(list_result)
    engin = sqlalchemy.create_engine("mysql+pymysql://sys_admin:Mysql_2023!@10.26.39.13:3306/crawling_download")
    results.to_sql("ct_cnipa_cs", con=engin, index=False, if_exists='append')


if __name__ == '__main__':
    for i in range(5, 6):
        data = {
            "wgViewmodle": "",
            "strWhere": "(( ((名称=((测试 AND 方法 OR 封测 OR 检测 OR (test OR testing) AND method) AND (晶圆 OR 晶元 OR wafer OR 晶粒)) NOT 名称=(设备 OR 装置 OR 系统 OR 材料 OR Equipment OR device OR system OR material) OR (名称=(测试 AND 方法 OR 封测 OR 检测 OR (test OR testing) AND method) AND 名称,摘要+=(晶圆 OR 晶元 OR wafer OR 晶粒)) NOT 名称=(设备 OR 装置 OR 检测器 OR 测试仪 OR 检测仪 OR Equipment OR device OR detector OR tester)) AND 分类号=('G01R31%' OR 'G06F11%' OR 'H01L21/66%')) OR  名称=((晶圆OR 晶片OR 晶圆OR 晶圆级 OR wafer) AND (测试 OR 检测 OR test OR detection) AND (接受 OR 验收OR 允收 OR Acceptance) OR Wafer Acceptance Test OR WAT testkey) OR 名称=(测试 AND 方法 OR 封测 OR 检测 OR (test OR testing) AND method) AND 名称=(MOS晶体管 OR 场效应晶体管 OR 金属电容 OR 多晶硅电容方块电阻 OR 接触电阻 OR 栅氧层 OR N结型 OR P结型 OR 'Sheet Resistance' OR 方块电阻 OR 'WAT') AND 分类号='H01L21/66%' OR 名称=((chipprobing OR chipprobe OR chip probing OR chip probe) AND test AND method OR 芯片 AND 探针 AND 测试 AND 方法 OR 芯片针测 AND 方法) OR (((名称=(测试 AND 方法 OR 封测 OR 检测 OR (test OR testing) AND method) AND 申请（专利权）人=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR 电路 AND 制造 OR integrated circuit OR microelectronics OR semiconductor OR chip OR circuit AND manufacturing) OR 名称=((测试 AND 方法 OR 封测 OR 检测 OR (test OR testing) AND method) AND (集成电路 OR 半导体 OR 芯片 OR 封装 OR 'IC' OR integrated circuit OR microelectronics OR semiconductor OR chip)) NOT 名称=(设备 OR 装置 OR 系统 OR 材料 OR Equipment OR device OR system OR material) OR 名称=(测试 AND 方法 OR 封测 OR 检测 OR (test OR testing) AND method) AND 名称,摘要+=(集成电路 OR 半导体 OR 芯片 OR 封装 OR 'IC' OR integrated circuit OR microelectronics OR semiconductor OR chip)) NOT 名称=(设备 OR 装置 OR 检测器 OR 测试仪 OR 检测仪 OR Equipment OR device OR detector OR tester)) AND 分类号=('G01R31%' OR 'G06F11%')) ) or ( ((名称=((测试 AND 方法 OR 封测 OR 检测 OR (test OR testing) AND method) AND (晶圆 OR 晶元 OR wafer OR 晶粒)) NOT 名称=(设备 OR 装置 OR 系统 OR 材料 OR Equipment OR device OR system OR material) OR (名称=(测试 AND 方法 OR 封测 OR 检测 OR (test OR testing) AND method) AND 名称,摘要+=(晶圆 OR 晶元 OR wafer OR 晶粒)) NOT 名称=(设备 OR 装置 OR 检测器 OR 测试仪 OR 检测仪 OR Equipment OR device OR detector OR tester)) AND 分类号=('G01R31%' OR 'G06F11%' OR 'H01L21/66%')) OR 名称=((晶圆OR 晶片OR 晶圆OR 晶圆级 OR wafer) AND (测试 OR 检测 OR test OR detection) AND (接受 OR 验收OR 允收 OR Acceptance) OR Wafer Acceptance Test OR WAT testkey) OR 名称=(测试 AND 方法 OR 封测 OR 检测 OR (test OR testing) AND method) AND 名称=(MOS晶体管 OR 场效应晶体管 OR 金属电容 OR 多晶硅电容方块电阻 OR 接触电阻 OR 栅氧层 OR N结型 OR P结型 OR 'Sheet Resistance' OR 方块电阻 OR 'WAT') AND 分类号='H01L21/66%' OR 名称=((chipprobing OR chipprobe OR chip probing OR chip probe) AND test AND method OR 芯片 AND 探针 AND 测试 AND 方法 OR 芯片针测 AND 方法) OR (((名称=(测试 AND 方法 OR 封测 OR 检测 OR (test OR testing) AND method) AND 申请（专利权）人=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR 电路 AND 制造 OR integrated circuit OR microelectronics OR semiconductor OR chip OR circuit AND manufacturing) OR 名称=((测试 AND 方法 OR 封测 OR 检测 OR (test OR testing) AND method) AND (集成电路 OR 半导体 OR 芯片 OR 封装 OR 'IC' OR integrated circuit OR microelectronics OR semiconductor OR chip)) NOT 名称=(设备 OR 装置 OR 系统 OR 材料 OR Equipment OR device OR system OR material) OR 名称=(测试 AND 方法 OR 封测 OR 检测 OR (test OR testing) AND method) AND 名称,摘要+=(集成电路 OR 半导体 OR 芯片 OR 封装 OR 'IC' OR integrated circuit OR microelectronics OR semiconductor OR chip)) NOT 名称=(设备 OR 装置 OR 检测器 OR 测试仪 OR 检测仪 OR Equipment OR device OR detector OR tester)) AND 分类号=('G01R31%' OR 'G06F11%')) ))  and 地址=(( (315%浙江省宁波市 or 浙江%宁波 or 宁波%海曙 or 浙江%海曙 or 宁波%江东 or 宁波%江北 or 宁波%北仑 or 浙江%北仑 or 宁波%镇海 or 浙江%镇海 or 宁波%鄞州 or 鄞县 or 浙江%慈溪 or 宁波%慈溪 or 慈溪县 or 浙江%余姚 or 宁波%余姚 or 余姚县 or 浙江%奉化 or 宁波%奉化 or 奉化县 or 浙江%宁海 or 宁波%宁海 or 浙江%象山 or 宁波%象山 or 宁波%国家高新区 or 宁波%科技园区 or 宁波%保税区 or 宁波%大榭开发区 or 宁波%东钱湖旅游度假区)))",
            "start": "{}".format(str(i)),
            "limit": "10",
            "option": "",
            "iHitPointType": "115",
            "strSortMethod": "RELEVANCE",
            "strSources": "FMZL,FMSQ,SYXX,WGZL,TWZL,HKPATENT,USPATENT,JPPATENT,EPPATENT,WOPATENT,GBPATENT,DEPATENT,FRPATENT,CHPATENT,KRPATENT,RUPATENT,APPATENT,ATPATENT,AUPATENT,ITPATENT,SEPATENT,CAPATENT,ESPATENT,GCPATENT,ASPATENT,OTHERPATENT",
            "strSynonymous": "",
            "yuyijs": "",
            "filterChannel": "",
            "keyword2Save": "( (315%浙江省宁波市 or 浙江%宁波 or 宁波%海曙 or 浙江%海曙 or 宁波%江东 or 宁波%江北 or 宁波%北仑 or 浙江%北仑 or 宁波%镇海 or 浙江%镇海 or 宁波%鄞州 or 鄞县 or 浙江%慈溪 or 宁波%慈溪 or 慈溪县 or 浙江%余姚 or 宁波%余姚 or 余姚县 or 浙江%奉化 or 宁波%奉化 or 奉化县 or 浙江%宁海 or 宁波%宁海 or 浙江%象山 or 宁波%象山 or 宁波%国家高新区 or 宁波%科技园区 or 宁波%保税区 or 宁波%大榭开发区 or 宁波%东钱湖旅游度假区))",
            "key2Save": "地址",
            "forward": "",
            "otherWhere": "",
            "username": "",
            "password": "",
            "fr": ""
        }
        run_sj(data)
    print('finish')
