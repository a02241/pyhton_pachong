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
    "Cookie": "JSESSIONID=D28F22D1561B1A1AD3D52B1C6151685C; Hm_lvt_1067a6b069a094a18ed1330087b6bbd1=1697612846; searchcol=%u5730%u5740; Hm_lpvt_1067a6b069a094a18ed1330087b6bbd1=1697613948",
    "Dnt": "1",
    "Host": "chinaip.cnipa.gov.cn",
    "Origin": "http://chinaip.cnipa.gov.cn",
    "Referer": "http://chinaip.cnipa.gov.cn/search!doOverviewSearch.action?type=navdb&db=all&id=3558_3613",
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
    results.to_sql("ct_cnipa_zz", con=engin, index=False, if_exists='append')


if __name__ == '__main__':

    for i in range(76, 119):
        data = {
            "wgViewmodle": "",
            "strWhere": "(( (((申请（专利权）人=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR 硅片 OR 电路 AND 制造 OR 台湾积体电路 OR 中芯国际 OR 上海华虹 OR Integrated circuit OR semiconductor OR circuit AND Manufacturing OR microelectronics OR chip) AND 名称=(制造 OR 制备 OR 制作 OR 生产 OR 工艺 OR 加工 OR Manufacturing OR Preparation OR Process OR producing OR processing)) NOT 名称=(设备 OR 装置 OR 系统 OR 二极管 OR 三极管 OR 晶体管 OR 场效应管 OR Equipment OR device OR system OR diode OR triode OR transistor OR 电池 OR battery)) AND 分类号=('H01L21%') OR 名称=((集成电路 OR 'Integrated circuit' OR 芯片 OR chip OR 微电路 OR microcircuit OR microchip) AND (制造 OR 制备 OR 制作 OR 生产 OR 工艺 OR 加工 OR Manufacturing OR Preparation OR Process OR producing OR processing)) AND 分类号=('H01L21%') OR ((名称,摘要+=(光刻 OR 曝光 OR 显影 OR 外延 OR 刻蚀 OR 蚀刻 OR CVD OR APCVD OR LPCVD OR PECVD OR PCVD OR SACVD OR MOCVD OR 化学气相淀积 OR 化学气相沉积 OR 化学汽相淀积 OR 化学汽相沉积 OR 等离子 AND 气相 OR 等离子 AND 反应 AND 气体 OR 常温化学气相 OR 低压化学气相 OR 'chemical vapor deposition' OR 薄膜沉积 OR 薄膜生长 OR Deposition AND Film OR Physical Vapor Deposition OR sputtering OR coating OR ion plating OR ion beam OR vacuum evaporation OR PVD OR 物理气相淀积 OR 物理气相沉积 OR 物理汽相沉积 OR 物理汽相淀积 OR 离子镀 OR 溅射 OR 蒸镀 OR 'Physical Vapor Deposition' OR PCVD OR 扩散 OR diffussing OR 离子注入 OR 'ion implantat%'OR 'ion implant%' OR 化学 AND 机械抛光 OR CMP OR chemical mechanical polishing OR 金属化 OR 激光退火 OR 金属层 OR 金属互连 OR 多层互连 OR 铜互连 OR lithography OR photolithographical OR lithographicc OR Photolithography OR Etching OR 'ion implantat%'or 'ion implant%' OR 'chemical vapor deposition' OR 'chemically vapor depositing' OR ALD OR 'Atomic layer deposition' OR 原子层沉积 OR 原子层外延 OR 'atomic layer epitaxy' OR 'chemical mechanical polishing' OR 铝互连 OR 'aluminium interconnect' OR Al互连 OR 铝布线互连 OR 'Al interconnect' OR 铜互连 OR copper interconnect OR CU互连 OR 铜布线互连) AND (名称,摘要+=(芯片 OR Chip OR 晶圆 OR 集成电路 OR 微电路 OR microchip OR 'Integrated circuit' OR 半导体 OR 衬底 OR 外延片 OR 晶片 OR 单晶 OR 晶圆 OR 晶元 OR 基底 OR 基片 OR 硅片 OR 基板 OR 外延层 OR 外延膜 OR wafer OR substrate OR 'epitaxial layer' OR 'epitaxial film' OR SOI OR semiconductor OR Epitaxial OR Epitaxy) OR 申请（专利权）人=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR 硅片 OR 电路 AND 制造 OR 联华电子 OR 力晶科技 OR 'Tower Jazz' OR Vanguard OR 华虹宏力 OR 长江存储 OR ASMC OR 华润上华 OR Intel OR Applied Materials OR 应用材料 OR TOKYO ELECTRON OR semiconductor OR wafer OR circuit AND Manufacturing OR UNITED MICROELECTRONICS OR powerchip or YANGTZE MEMORY OR CSMC OR CHIP)) AND 名称,摘要+=(制造 OR 制备 OR 制作 OR 生产 OR 工艺 OR 加工 OR Manufacturing OR Preparation OR Process OR producing OR processing)) NOT 名称=(装置 OR 设备 OR 系统 OR 材料 OR 胶 OR 液 OR 垫 OR 剂 OR 组合物 OR 台 OR 二极管 OR 三极管 OR 晶体管 OR 场效应管 OR 封装 OR device OR system OR material OR glue OR liquid OR pad OR agent OR composition OR table OR diode OR triode OR transistor OR packag% OR 电池 OR battery)) AND 分类号=('H01L21%' OR 'C23C14%' OR 'C23C16%') OR 申请（专利权）人=(联华电子 OR 力晶科技 OR ' Tower Semiconductor' OR 高塔半导体 OR 威兆半导体 OR Vanguard OR 华虹宏力 OR 长江存储 OR 上海先进半导体 OR ASMC OR 华润上华 OR 上海华力微电子 OR Intel OR MICROELECTRONI OR UNITED MICROELECTRONICS OR powerchip or YANGTZE MEMORY OR CSMC OR SHANGHAI HUAHONG GRACE) AND 分类号=('H01L21%' OR 'C23C14%' OR 'C23C16%')) OR 主分类号='C30B15/%' NOT 名称=(装置 OR 装备 OR 设备 OR Apparatus OR device OR 容器 OR 支架 OR 旋转头 OR 'Rotating head' OR 坩埚 OR 夹持器 OR 炉 OR furnace OR 系统 OR system OR 机构 OR Vessel OR mechanism OR 测试) OR 主分类号='C30B15/%' AND 名称=(工艺 OR 方法 Method) OR (名称=(拉晶) OR 名称=(pulling OR 拉) AND 名称=(工艺 OR 方法 Method) AND 名称,摘要+=(硅 OR 晶 OR crystal OR silicon OR Wafer) AND 分类号='C30%') OR ((名称=(扩散 OR diffus%) AND 申请（专利权）人=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR 电路 AND 制造 OR wafer OR 'integrated circuit' OR microelectronics OR semiconductor OR chip OR circuit AND manufacturing) OR 名称=((扩散 OR diffus%) AND (方法 OR 工艺 OR 杂质 OR Method OR impurity%)) AND 分类号=('H01L21/336%' OR 'H01L21/223%' OR 'H01L21/225%')) NOT 名称=(电池 OR Battery)) OR 名称=((氧化 OR oxid%) AND (方法 OR Method OR 工艺)) AND 名称,摘要+=(硅 OR 晶片 OR 晶圆 OR silicon OR Wafer OR 半导体 OR 晶元 OR semiconductor) AND 主分类号=('H01L21/316%' OR 'H01L21/31%' OR 'H01L21/02%') OR 名称=((氧化 OR oxid%) AND (方法 OR Method OR 工艺)) AND 名称,摘要+=(硅片 OR 晶片 OR 晶圆 OR Wafer OR 晶元 OR semiconductor) AND 分类号='H01L21%' NOT 主分类号='H01L21/66%' OR (主分类号='C30B%' NOT 名称=(装置 OR 装备 OR 设备 OR Apparatus OR device OR 容器 OR 支架 OR 旋转头 OR 'Rotating head' OR 坩埚 OR 夹持器 OR 炉 OR furnace OR 系统 OR system OR 机构 OR Vessel OR mechanism OR 测试) OR 主分类号='C30B%' AND 名称=(工艺 OR 方法 OR Method OR Process) OR 名称,摘要+=(单晶 OR 'single crystal' OR monocrystalline OR monocrystal) AND 名称=(工艺 OR 方法 OR Method OR Process) AND 主分类号='C30%') AND 名称,摘要,权利要求书,说明书+=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR IC OR Microelectronics OR Semiconductor OR Chip OR 'Integrated circuit' OR wafer) OR 名称=(外延生长 OR 外延结构 OR 外延层 OR Epitaxial OR Epitaxy) NOT 名称=(二极管 OR LED OR 设备 OR 装置 OR 炉 OR 系统 OR 盒 OR 激光器 OR Apparatus OR device OR furnace OR system OR diode OR Box OR laser OR 探测器) AND 主分类号=('H01L%' OR 'C30B%') OR 名称=(外延 OR Epitaxial OR Epitaxy) NOT 名称=(二极管 OR LED OR 设备 OR 装置 OR 炉 OR 系统 OR 盒 OR 激光器 OR Apparatus OR device OR furnace OR system OR diode OR Box OR laser) AND 名称,摘要+=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR IC OR Microelectronics OR Semiconductor OR Chip OR 'Integrated circuit' OR wafer OR 单晶 OR 'single crystal' OR monocrystalline OR monocrystal) OR 名称=(外延 OR Epitaxial OR Epitaxy) AND 名称=(方法 OR 工艺 OR method OR Process) AND 名称,摘要+=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR IC OR Microelectronics OR Semiconductor OR Chip OR 'Integrated circuit' OR wafer OR 单晶 OR 'single crystal' OR monocrystalline OR monocrystal) NOT 名称,摘要+=(二极管 OR LED OR diode) OR 名称=(热处理 OR 退火 OR 淬火 OR heat treatment OR annealing OR quench) AND 名称,摘要+=( 晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 AND 基板 OR Microelectronics OR Semiconductor AND Substrate OR 'Integrated circuit' OR wafer OR 晶片 OR 硅片) AND 名称=(方法 OR method OR process) NOT 名称,摘要+=(电池 OR 太阳能 OR Battery OR Solar) OR 申请（专利权）人=(集成电路 OR 微电子 OR 芯片 OR 电路 AND 制造 OR Microelectronics OR Chip OR Circuit AND Manufacturing OR integrated circuit) AND 分类号='H01L21%' ) or ( (((申请（专利权）人=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR 硅片 OR 电路 AND 制造 OR 台湾积体电路 OR 中芯国际 OR 上海华虹 OR Integrated circuit OR semiconductor OR circuit AND Manufacturing OR microelectronics OR chip) AND 名称=(制造 OR 制备 OR 制作 OR 生产 OR 工艺 OR 加工 OR Manufacturing OR Preparation OR Process OR producing OR processing)) NOT 名称=(设备 OR 装置 OR 系统 OR 二极管 OR 三极管 OR 晶体管 OR 场效应管 OR Equipment OR device OR system OR diode OR triode OR transistor OR 电池 OR battery)) AND 分类号=('H01L21%') OR 名称=((集成电路 OR 'Integrated circuit' OR 芯片 OR chip OR 微电路 OR microcircuit OR microchip) AND (制造 OR 制备 OR 制作 OR 生产 OR 工艺 OR 加工 OR Manufacturing OR Preparation OR Process OR producing OR processing)) AND 分类号=('H01L21%') OR ((名称,摘要+=(光刻 OR 曝光 OR 显影 OR 外延 OR 刻蚀 OR 蚀刻 OR CVD OR APCVD OR LPCVD OR PECVD OR PCVD OR SACVD OR MOCVD OR 化学气相淀积 OR 化学气相沉积 OR 化学汽相淀积 OR 化学汽相沉积 OR 等离子 AND 气相 OR 等离子 AND 反应 AND 气体 OR 常温化学气相 OR 低压化学气相 OR 'chemical vapor deposition' OR 薄膜沉积 OR 薄膜生长 OR Deposition AND Film OR Physical Vapor Deposition OR sputtering OR coating OR ion plating OR ion beam OR vacuum evaporation OR PVD OR 物理气相淀积 OR 物理气相沉积 OR 物理汽相沉积 OR 物理汽相淀积 OR 离子镀 OR 溅射 OR 蒸镀 OR 'Physical Vapor Deposition' OR PCVD OR 扩散 OR diffussing OR 离子注入 OR 'ion implantat%'OR 'ion implant%' OR 化学 AND 机械抛光 OR CMP OR chemical mechanical polishing OR 金属化 OR 激光退火 OR 金属层 OR 金属互连 OR 多层互连 OR 铜互连 OR lithography OR photolithographical OR lithographicc OR Photolithography OR Etching OR 'ion implantat%'or 'ion implant%' OR 'chemical vapor deposition' OR 'chemically vapor depositing' OR ALD OR 'Atomic layer deposition' OR 原子层沉积 OR 原子层外延 OR 'atomic layer epitaxy' OR 'chemical mechanical polishing' OR 铝互连 OR 'aluminium interconnect' OR Al互连 OR 铝布线互连 OR 'Al interconnect' OR 铜互连 OR copper interconnect OR CU互连 OR 铜布线互连) AND (名称,摘要+=(芯片 OR Chip OR 晶圆 OR 集成电路 OR 微电路 OR microchip OR 'Integrated circuit' OR 半导体 OR 衬底 OR 外延片 OR 晶片 OR 单晶 OR 晶圆 OR 晶元 OR 基底 OR 基片 OR 硅片 OR 基板 OR 外延层 OR 外延膜 OR wafer OR substrate OR 'epitaxial layer' OR 'epitaxial film' OR SOI OR semiconductor OR Epitaxial OR Epitaxy) OR 申请（专利权）人=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR 硅片 OR 电路 AND 制造 OR 联华电子 OR 力晶科技 OR 'Tower Jazz' OR Vanguard OR 华虹宏力 OR 长江存储 OR ASMC OR 华润上华 OR Intel OR Applied Materials OR 应用材料 OR TOKYO ELECTRON OR semiconductor OR wafer OR circuit AND Manufacturing OR UNITED MICROELECTRONICS OR powerchip or YANGTZE MEMORY OR CSMC OR CHIP)) AND 名称,摘要+=(制造 OR 制备 OR 制作 OR 生产 OR 工艺 OR 加工 OR Manufacturing OR Preparation OR Process OR producing OR processing)) NOT 名称=(装置 OR 设备 OR 系统 OR 材料 OR 胶 OR 液 OR 垫 OR 剂 OR 组合物 OR 台 OR 二极管 OR 三极管 OR 晶体管 OR 场效应管 OR 封装 OR device OR system OR material OR glue OR liquid OR pad OR agent OR composition OR table OR diode OR triode OR transistor OR packag% OR 电池 OR battery)) AND 分类号=('H01L21%' OR 'C23C14%' OR 'C23C16%') OR 申请（专利权）人=(联华电子 OR 力晶科技 OR ' Tower Semiconductor' OR 高塔半导体 OR 威兆半导体 OR Vanguard OR 华虹宏力 OR 长江存储 OR 上海先进半导体 OR ASMC OR 华润上华 OR 上海华力微电子 OR Intel OR MICROELECTRONI OR UNITED MICROELECTRONICS OR powerchip or YANGTZE MEMORY OR CSMC OR SHANGHAI HUAHONG GRACE) AND 分类号=('H01L21%' OR 'C23C14%' OR 'C23C16%')) OR 主分类号='C30B15/%' NOT 名称=(装置 OR 装备 OR 设备 OR Apparatus OR device OR 容器 OR 支架 OR 旋转头 OR 'Rotating head' OR 坩埚 OR 夹持器 OR 炉 OR furnace OR 系统 OR system OR 机构 OR Vessel OR mechanism OR 测试) OR 主分类号='C30B15/%' AND 名称=(工艺 OR 方法 Method) OR (名称=(拉晶) OR 名称=(pulling OR 拉) AND 名称=(工艺 OR 方法 Method) AND 名称,摘要+=(硅 OR 晶 OR crystal OR silicon OR Wafer) AND 分类号='C30%') OR ((名称=(扩散 OR diffus%) AND 申请（专利权）人=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR 电路 AND 制造 OR wafer OR 'integrated circuit' OR microelectronics OR semiconductor OR chip OR circuit AND manufacturing) OR 名称=((扩散 OR diffus%) AND (方法 OR 工艺 OR 杂质 OR Method OR impurity%)) AND 分类号=('H01L21/336%' OR 'H01L21/223%' OR 'H01L21/225%')) NOT 名称=(电池 OR Battery)) OR 名称=((氧化 OR oxid%) AND (方法 OR Method OR 工艺)) AND 名称,摘要+=(硅 OR 晶片 OR 晶圆 OR silicon OR Wafer OR 半导体 OR 晶元 OR semiconductor) AND 主分类号=('H01L21/316%' OR 'H01L21/31%' OR 'H01L21/02%') OR 名称=((氧化 OR oxid%) AND (方法 OR Method OR 工艺)) AND 名称,摘要+=(硅片 OR 晶片 OR 晶圆 OR Wafer OR 晶元 OR semiconductor) AND 分类号='H01L21%' NOT 主分类号='H01L21/66%' OR (主分类号='C30B%' NOT 名称=(装置 OR 装备 OR 设备 OR Apparatus OR device OR 容器 OR 支架 OR 旋转头 OR 'Rotating head' OR 坩埚 OR 夹持器 OR 炉 OR furnace OR 系统 OR system OR 机构 OR Vessel OR mechanism OR 测试) OR 主分类号='C30B%' AND 名称=(工艺 OR 方法 OR Method OR Process) OR 名称,摘要+=(单晶 OR 'single crystal' OR monocrystalline OR monocrystal) AND 名称=(工艺 OR 方法 OR Method OR Process) AND 主分类号='C30%') AND 名称,摘要,权利要求书,说明书+=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR IC OR Microelectronics OR Semiconductor OR Chip OR 'Integrated circuit' OR wafer) OR 名称=(外延生长 OR 外延结构 OR 外延层 OR Epitaxial OR Epitaxy) NOT 名称=(二极管 OR LED OR 设备 OR 装置 OR 炉 OR 系统 OR 盒 OR 激光器 OR Apparatus OR device OR furnace OR system OR diode OR Box OR laser OR 探测器) AND 主分类号=('H01L%' OR 'C30B%') OR 名称=(外延 OR Epitaxial OR Epitaxy) NOT 名称=(二极管 OR LED OR 设备 OR 装置 OR 炉 OR 系统 OR 盒 OR 激光器 OR Apparatus OR device OR furnace OR system OR diode OR Box OR laser) AND 名称,摘要+=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR IC OR Microelectronics OR Semiconductor OR Chip OR 'Integrated circuit' OR wafer OR 单晶 OR 'single crystal' OR monocrystalline OR monocrystal) OR 名称=(外延 OR Epitaxial OR Epitaxy) AND 名称=(方法 OR 工艺 OR method OR Process) AND 名称,摘要+=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR IC OR Microelectronics OR Semiconductor OR Chip OR 'Integrated circuit' OR wafer OR 单晶 OR 'single crystal' OR monocrystalline OR monocrystal) NOT 名称,摘要+=(二极管 OR LED OR diode) OR 名称=(热处理 OR 退火 OR 淬火 OR heat treatment OR annealing OR quench) AND 名称,摘要+=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 AND 基板 OR Microelectronics OR Semiconductor AND Substrate OR 'Integrated circuit' OR wafer OR 晶片 OR 硅片) AND 名称=(方法 OR method OR process) NOT 名称,摘要+=(电池 OR 太阳能 OR Battery OR Solar) OR 申请（专利权）人=(集成电路 OR 微电子 OR 芯片 OR 电路 AND 制造 OR Microelectronics OR Chip OR Circuit AND Manufacturing OR integrated circuit) AND 分类号='H01L21%' ))  and 地址=(( (315%浙江省宁波市 or 浙江%宁波 or 宁波%海曙 or 浙江%海曙 or 宁波%江东 or 宁波%江北 or 宁波%北仑 or 浙江%北仑 or 宁波%镇海 or 浙江%镇海 or 宁波%鄞州 or 鄞县 or 浙江%慈溪 or 宁波%慈溪 or 慈溪县 or 浙江%余姚 or 宁波%余姚 or 余姚县 or 浙江%奉化 or 宁波%奉化 or 奉化县 or 浙江%宁海 or 宁波%宁海 or 浙江%象山 or 宁波%象山 or 宁波%国家高新区 or 宁波%科技园区 or 宁波%保税区 or 宁波%大榭开发区 or 宁波%东钱湖旅游度假区)))",
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
