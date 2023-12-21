
import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlalchemy

# 请求头
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Content-Length": "78459",
    "Content-Type": "application/x-www-form-urlencoded",
    "Cookie": "Hm_lvt_1067a6b069a094a18ed1330087b6bbd1=1697612846; searchcol=%u5730%u5740; JSESSIONID=19E0E2DFC910B74CCE41F4434AE8D11E; Hm_lpvt_1067a6b069a094a18ed1330087b6bbd1=1697618253",
    "Dnt": "1",
    "Host": "chinaip.cnipa.gov.cn",
    "Origin": "http://chinaip.cnipa.gov.cn",
    "Referer": "http://chinaip.cnipa.gov.cn/search!doOverviewSearch.action?type=navdb&db=all&id=3558_3641",
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
    results.to_sql("ct_cnipa_fz", con=engin, index=False, if_exists='append')


if __name__ == '__main__':

    for i in range(29, 93):
        data = {
            "wgViewmodle": "",
            "strWhere": "(( 申请（专利权）人=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR 电路 AND 制造 OR 封装 OR 日月光 OR 安靠 OR Amkor OR 长电 OR 矽品 OR 力成 OR 天水华天 OR 南通富士通 OR 富微电子 OR 台湾 AND 京元 OR 联测 OR 南茂科技 OR 联合科技 OR nepes OR 晶方半导体 OR 气派科技 OR 风华芯电 OR 华天科技 OR wafer OR Integrated circuit OR Microelectronics OR Semiconductor OR Chip OR Circuit AND Manufacturing OR Packaging OR ADVANCED SEMICONDUCTOR OR SILICONWARE PRECISION OR PEGATRON CORPORATION OR SAMSUNG OR 精材科技 OR XINTEC) AND 名称,摘要+=(封装 OR 封测 OR packag% OR encapsulat% OR 倒装 OR 贴装) AND 分类号=('H01L21%' OR 'H01L23%') OR 名称=(封装 OR 封测 OR packag% OR encapsulat% OR 倒装 OR 贴装) AND 分类号=('H01L21/56%' OR 'H01L23/28%' OR 'H01L33/48%') OR 名称=((封装 OR 封测 OR packag% OR encapsulat%)) AND 名称,摘要+=(芯片 OR Chip OR 晶圆 OR 集成电路 OR 'Integrated circuit' OR 半导体 OR 晶片 OR WAFER OR Semiconductor) AND 分类号=('H01L%') OR 名称,摘要+=(双列直插 OR  DIP OR Dual In-line Package OR Dual In line Package OR单列直插 OR  SIP OR single in-line ORsingle In line OR SOT OR 小外形 AND 晶体管 OR 'SmallOut-LineTransistor' OR 'Small Out Line Transistor' OR 'Small Out-Line Transistor' OR 'Small Out-Line Package' OR 'Small Out  Line Package' OR SOP OR 小外形 OR SOJ OR TSOP OR VSOP OR SSOP OR TSSOP OR SOL OR DFP OR 四方扁平 OR 引脚扁平 OR QFP OR 'Quad Flat'  OR 四方粒 OR 扁平式封装 OR 小型方块平面 or 方形扁平 OR PLCC OR 塑料 AND 引线 AND 载体 OR Plastic Leaded Chip Carrier OR 双边扁平 OR DFN OR quad flat no-lead OR quad flat no lead OR QFN OR 四面 AND 无引脚 OR 扁平无引脚 OR BGA OR 球栅阵列 OR 焊球阵列 OR 'Ball grid array' OR 球门阵列 OR 焊球凸点 OR PBGA OR CBGA OR FCBGA OR CDPBGA OR SIP OR 系统级 OR 'system in package' OR ' system level' OR 'system-in-package' OR 'system in a' OR 系统封装 OR 晶圆级 OR WLP OR WLCSP OR 晶片级 OR wafer level OR 晶圆片级 OR芯片尺寸 OR CSP OR chip scale OR 芯片级 OR MCP OR 多芯片 AND 封装 OR 'multi chip' OR 'multiple chip' OR 晶圆级封装 OR 'Wafer Level Packaging' OR WLP OR Bumping OR 凸点 OR 凸块 OR 倒装芯片 OR flip-chip OR 'Flip chip' OR 扇出 OR FOWLP OR 'Fan-out Wafer Level' OR 系统级单芯片 OR 系统单芯片 OR SOC OR 'System-on-a-chip' OR TSV OR 硅通孔 OR 'through silicon via' OR 硅导通孔 OR 硅穿孔 OR 衬底通孔 OR TSVs OR 3D AND 堆叠 OR 3D stack% OR 3维 AND 堆叠 OR 3维 AND 叠层 OR 'Three Dimensional stack%' OR '3D packa%' OR 立体堆叠 OR 堆叠封装) AND 分类号='H01L%' OR 名称=(封装 OR 封测 OR  Package OR Packaging) AND 名称,摘要+=(2.5D OR interposer OR RDL OR Redistributionlayer OR 再分布层 OR Interposer) AND 分类号=('H01L21%' OR 'H01L23%') OR 名称=((封装 OR 封测 OR packag% OR encapsulat% OR 倒装 OR 贴装) AND (方法 OR 工艺 OR 技术 OR 结构 OR 格式 OR Method OR Process OR Technology OR Structure OR Format)) AND 名称,摘要+=(2.5D OR interposer OR RDL OR Redistributionlayer OR 再分布层 OR Interposer) AND 分类号='H%' ) or ( 申请（专利权）人=(晶圆 OR 晶元 OR 集成电路 OR 微电子 OR 半导体 OR 芯片 OR 电路 AND 制造 OR 封装 OR 日月光 OR 安靠 OR Amkor OR 长电 OR 矽品 OR 力成 OR 天水华天 OR 南通富士通 OR 富微电子 OR 台湾 AND 京元 OR 联测 OR 南茂科技 OR 联合科技 OR nepes OR 晶方半导体 OR 气派科技 OR 风华芯电 OR 华天科技 OR wafer OR Integrated circuit OR Microelectronics OR Semiconductor OR Chip OR Circuit AND Manufacturing OR Packaging OR ADVANCED SEMICONDUCTOR OR SILICONWARE PRECISION OR PEGATRON CORPORATION OR SAMSUNG OR 精材科技 OR XINTEC) AND 名称,摘要+=(封装 OR 封测 OR packag% OR encapsulat% OR 倒装 OR 贴装) AND 分类号=('H01L21%' OR 'H01L23%') OR 名称=(封装 OR 封测 OR packag% OR encapsulat% OR 倒装 OR 贴装) AND 分类号=('H01L21/56%' OR 'H01L23/28%' OR 'H01L33/48%') OR 名称=((封装 OR 封测 OR packag% OR encapsulat%)) AND 名称,摘要+=(芯片 OR Chip OR 晶圆 OR 集成电路 OR 'Integrated circuit' OR 半导体 OR 晶片 OR WAFER OR Semiconductor) AND 分类号=('H01L%') OR 名称,摘要+=(双列直插 OR  DIP OR Dual In-line Package OR Dual In line Package OR单列直插 OR  SIP OR single in-line ORsingle In line OR SOT OR 小外形 AND 晶体管 OR 'SmallOut-LineTransistor' OR 'Small Out Line Transistor' OR 'Small Out-Line Transistor' OR 'Small Out-Line Package' OR 'Small Out  Line Package' OR SOP OR 小外形 OR SOJ OR TSOP OR VSOP OR SSOP OR TSSOP OR SOL OR DFP OR 四方扁平 OR 引脚扁平 OR QFP OR 'Quad Flat'  OR 四方粒 OR 扁平式封装 OR 小型方块平面 or 方形扁平 OR PLCC OR 塑料 AND 引线 AND 载体 OR Plastic Leaded Chip Carrier OR 双边扁平 OR DFN OR quad flat no-lead OR quad flat no lead OR QFN OR 四面 AND 无引脚 OR 扁平无引脚 OR BGA OR 球栅阵列 OR 焊球阵列 OR 'Ball grid array' OR 球门阵列 OR 焊球凸点 OR PBGA OR CBGA OR FCBGA OR CDPBGA OR SIP OR 系统级 OR 'system in package' OR ' system level' OR 'system-in-package' OR 'system in a' OR 系统封装 OR 晶圆级 OR WLP OR WLCSP OR 晶片级 OR wafer level OR 晶圆片级 OR芯片尺寸 OR CSP OR chip scale OR 芯片级 OR MCP OR 多芯片 AND 封装 OR 'multi chip' OR 'multiple chip' OR 晶圆级封装 OR 'Wafer Level Packaging' OR WLP OR Bumping OR 凸点 OR 凸块 OR 倒装芯片 OR flip-chip OR 'Flip chip' OR 扇出 OR FOWLP OR 'Fan-out Wafer Level' OR 系统级单芯片 OR 系统单芯片 OR SOC OR 'System-on-a-chip' OR TSV OR 硅通孔 OR 'through silicon via' OR 硅导通孔 OR 硅穿孔 OR 衬底通孔 OR TSVs OR 3D AND 堆叠 OR 3D stack% OR 3维 AND 堆叠 OR 3维 AND 叠层 OR 'Three Dimensional stack%' OR '3D packa%' OR 立体堆叠 OR 堆叠封装) AND 分类号='H01L%' OR 名称=(封装 OR 封测 OR  Package OR Packaging) AND 名称,摘要+=(2.5D OR interposer OR RDL OR Redistributionlayer OR 再分布层 OR Interposer) AND 分类号=('H01L21%' OR 'H01L23%') OR 名称=((封装 OR 封测 OR packag% OR encapsulat% OR 倒装 OR 贴装) AND (方法 OR 工艺 OR 技术 OR 结构 OR 格式 OR Method OR Process OR Technology OR Structure OR Format)) AND 名称,摘要+=(2.5D OR interposer OR RDL OR Redistributionlayer OR 再分布层 OR Interposer) AND 分类号='H%' ))  and 地址=(( (315%浙江省宁波市 or 浙江%宁波 or 宁波%海曙 or 浙江%海曙 or 宁波%江东 or 宁波%江北 or 宁波%北仑 or 浙江%北仑 or 宁波%镇海 or 浙江%镇海 or 宁波%鄞州 or 鄞县 or 浙江%慈溪 or 宁波%慈溪 or 慈溪县 or 浙江%余姚 or 宁波%余姚 or 余姚县 or 浙江%奉化 or 宁波%奉化 or 奉化县 or 浙江%宁海 or 宁波%宁海 or 浙江%象山 or 宁波%象山 or 宁波%国家高新区 or 宁波%科技园区 or 宁波%保税区 or 宁波%大榭开发区 or 宁波%东钱湖旅游度假区)))",
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
