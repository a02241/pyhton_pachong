
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
    "Cookie": "Hm_lvt_1067a6b069a094a18ed1330087b6bbd1=1697612846; searchcol=%u5730%u5740; JSESSIONID=28CACC6F0BCB18980EF12C65C32AAE32; Hm_lpvt_1067a6b069a094a18ed1330087b6bbd1=1697622080",
    "Dnt": "1",
    "Host": "chinaip.cnipa.gov.cn",
    "Origin": "http://chinaip.cnipa.gov.cn",
    "Referer": "http://chinaip.cnipa.gov.cn/search!doOverviewSearch.action?type=navdb&db=all&id=3558_3678",
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
    results.to_sql("ct_cnipa_cl", con=engin, index=False, if_exists='append')


if __name__ == '__main__':

    for i in range(1, 160):
        data = {
            "wgViewmodle": "",
            "strWhere": "(( (名称=(氮气 OR 氧气 OR 氢气 OR 氦气 OR 三氯化硼 OR 三氟化硼 OR 三氟化磷 OR 砷化氢 OR 砷化三氢 or 六氟化硫 OR 四氟化碳 OR 氯化氢 OR 氟代甲烷 OR 氟化氮 OR 一氧化碳 OR 二氧化碳 OR 六氟乙烷 OR 全氟丙烷 OR 氟环丁烷 OR 三氟甲烷 OR 二氟甲烷 OR 氟甲烷 OR 氯气 OR 三氟化氯 OR HBr OR 溴化氢 OR HCl OR 氯化氢 OR HF OR 氟化氢 OR C2ClF5 OR 五氟一氯乙烷)) AND (名称=(生产 OR 制备 OR 提纯 OR 纯化)) AND (名称=(方法 OR 工艺)) AND (名称,摘要+=(电子级 OR 集成电路 OR 半导体 OR 晶圆 OR 晶元 OR 集成电路 OR 半导体 OR 芯片 OR 晶片 OR 微电子)) OR (名称=(气体) AND 名称=(电子级 OR 高纯 OR 超纯 OR MO源)) AND 名称,摘要+=(方法 OR 工艺) OR (名称=((高纯 OR 超纯 OR 电子级 OR 超净) AND (氢氧化铵 OR 氟化铵 OR 氢氧化钾 OR 硫酸 OR 氨水 OR 氧化氢 OR 硝酸 OR 醋酸 OR 盐酸 OR 硝酸 OR 氢氧 OR 双氧水 OR 氢氟酸 OR 氧化铵 OR 丙酮 OR 氨水 OR 氢氟酸 OR 磷酸 OR 乙酸 OR 乙二酸 OR 氢氧化钠 OR NaOH OR KOH OR 氢氧化钾 OR 四甲基氢氧化铵 OR 甲醇 OR 乙醇 OR 丙醇 OR 丙酮 OR 丁酮 OR 丁基酮 OR 乙酯 OR 丁酯 OR 戊酯 OR 苯 AND 试剂 OR 双氧水 OR 过氧化氢 OR 四氯化碳 OR 试剂 OR 溶液 OR 液体 OR 溶剂 OR 湿电子化学品)) AND 分类号=('C01B%' OR 'C01C%' OR 'C07C%')) AND 名称,摘要,权利要求书,说明书+=(晶圆 OR 晶元 OR 集成电路 OR 半导体 OR 芯片 OR 晶片 OR 微电子) OR 名称=(显影液 OR 显影剂 OR 漂洗液 OR 漂洗剂 OR 剥离液 OR 剥离剂 OR 去边液 OR 去边剂 OR 稀释剂 OR 稀释液 OR 清洗液 OR 刻蚀液) AND 名称,摘要+=(光刻胶 OR 光致抗蚀剂 OR 晶圆 OR 晶元 OR 集成电路 OR 半导体 OR 芯片 OR 晶片 OR 微电子) OR (名称=((硅 OR SOI) AND (衬底 OR 外延 OR 晶片 OR 单晶 OR 晶圆 OR 晶元 OR 基底 OR 基片 OR 硅片 OR 基板 OR 晶棒 OR 晶片 OR 半导体)) AND 名称=(制造 OR 制备 OR 制作 OR 生产 OR 工艺 OR 加工 OR 生长 OR 形成) AND 分类号=('C30B29/06%' OR 'C30B25/02%' OR 'H01L21/205%' OR 'C30B23/00%' OR 'H01L21/20%' OR 'H01L21/02%') OR 申请（专利权）人=(新阳 OR 郑州 AND 合晶 OR 金瑞泓 OR 有研 OR 信越化学 OR SUMCO OR 环球晶圆) AND 名称=(硅 OR 'si' OR SOI) AND 主分类号=('H01L%' OR 'C30B%')) NOT 名称,摘要+=(多晶 OR 太阳能 OR 碳化硅 OR SIC OR 炉 OR 设备 OR 装置) OR (名称=((砷化镓 OR GaAs OR 氮化镓 OR GaN OR 碳化硅 OR SiC OR '炭化けい素') AND (衬底 OR 外延 OR 晶片 OR 单晶 OR 晶圆 OR 晶元 OR 基底 OR 基片 OR 硅片 OR 基板 OR 晶棒 OR 晶体 OR 半导体 OR 薄膜)) AND (名称=(制造 OR 制备 OR 制作 OR 生产 OR 工艺 OR 加工 OR 生长 OR 形成) OR 分类号=('C30B29/42%' OR 'C30B29/38%')) OR 申请（专利权）人=(三安光电 OR 乾照光电 OR 南大光电 OR 海特高新 OR 云南诸业 OR 有研 OR 北京双仪微电子 OR 北京泛德辰 OR 中科晶电 OR 中科镓英 OR 国瑞电子 OR 新光电科技 OR 磊晶 OR 国瑞电子 OR 纳维科技 OR 东莞中镓 OR 苏州晶湛 OR 聚能晶源 OR 青岛聚能创芯微电子 OR 世纪金光 OR 中晶半导体 OR 英诺赛科 OR 三安集成 OR 苏州能讯 OR 江苏能华微电子 OR 江苏华功 OR 大连芯冠 OR 苏州捷芯威 OR 华润微电子 OR 士兰微 OR 海威华芯 OR 天岳 OR Cree OR 新日铁住金 OR 英飞凌 OR 瀚天天成 OR 天域 OR 中国电子科技集团)) AND 名称=(砷化镓 OR GaAs OR 氮化镓 OR 碳化硅) OR (((名称=(光刻胶 AND 组合物) AND 分类号=('G03F7%' OR 'G03C1%')) OR 名称=(光刻胶) AND 分类号=('G03F7/004%' OR 'G03C1/492%') OR 申请（专利权）人=(苏州瑞红 OR 北京科华 OR 星泰克 OR 晶瑞 OR JSR OR TOKYO OR 陶氏 OR 住友 OR 信越) AND 名称=(光刻胶) AND 分类号=('G03F7%' OR 'G03C1%'))) NOT 名称=(去除 OR 剥离 OR 装置 OR 设备 OR 涂敷) OR ((名称=(掩膜版 OR 光掩膜 OR 光刻版)) AND (名称=(基板 OR 结构 OR 图案 OR 图形 OR 制版 OR 设计 OR 形成 OR 布局 OR 制造 OR 制备 OR 制作 OR 生产 OR 工艺 OR 加工)) AND 分类号=('G03F1%' OR 'H01L21/027%' OR 'G03F7%') OR 名称=((光罩) AND (基板 OR 结构 OR 图案 OR 图形 OR 制版 OR 设计 OR 形成 OR 布局 OR 制造 OR 制备 OR 制作 OR 生产 OR 工艺 OR 加工)) AND 分类号=('H01L21/027%' OR 'G03F1/00%' OR 'G03F7/20%' OR 'G03F7/00%') OR 名称=(掩膜) AND 申请（专利权）人=(LG OR 福尼克斯 OR DNP OR Toppan OR 台湾光罩 OR 路维光电 OR 清溢精密or 无锡 AND 华润 OR 迪思微 OR SHASHIN KAGAKU)) OR 名称=((化学 AND 机械抛光 OR CMP) AND (组合物 OR 液 OR 浆)) OR 名称=(抛光液 OR 抛光剂 OR 抛光溶液 OR 粗抛液) AND 名称,摘要+=(晶圆 OR 晶元 OR 集成电路 OR 半导体 OR 芯片) OR 名称=(抛光液 OR 抛光剂 OR 抛光溶液 OR 粗抛液) AND 名称,摘要+=(晶圆 OR 晶元 OR 集成电路 OR 半导体 OR 芯片 OR 电路 AND 制造) AND 分类号=('C09K3/14%' OR 'C09G1/02%' OR 'B24B37/24%' OR 'B24B37/20%') OR (名称=(溅射 AND (靶材 OR (靶材 OR (铂 OR 钌 OR 铝 OR 钛 OR 钴  OR 镍 OR 钽 OR 铜  OR 金 OR 银 OR 合金)) AND 靶)) OR 申请（专利权）人=(日矿 OR 'JX NIPPON' OR 霍尼韦尔 OR Honeywell OR 东曹 OR TOSOH OR 普莱克斯 OR PREX OR 江丰电子 OR 有研 OR 阿石创 OR 隆华节能 OR 三菱 OR 'MITSUBISHI MATERIALS') AND 名称=(靶材)) OR (名称=(研磨液 OR 研磨剂 OR 研磨组合物) AND 名称,摘要+=(晶圆 OR 晶元 OR 集成电路 OR 半导体 OR 芯片 OR 晶片) OR 申请（专利权）人=(Cabot OR Nalco OR Rodel OR DuPont OR Grace OR Akzol Nobel OR Bayer OR Wacker OR Fujimi OR Fujifilm OR Nissan Chemical OR Fuso) AND 名称=(研磨液 OR 研磨剂 OR 研磨组合物)) NOT 名称=(装置 OR 设备 OR 槽) OR 名称=((蓝宝石 OR 金属氧化物) AND (衬底 OR 外延 OR 晶片 OR 单晶 OR 晶圆 OR 晶元 OR 基底 OR 基片 OR 硅片 OR 基板 OR 晶棒 OR 晶片) AND (制造 OR 制备 OR 制作 OR 生产 OR 工艺 OR 加工 OR 生长 OR 形成)) NOT 名称=(器件 OR 装置 OR 设备 OR 坩埚) OR 名称=(蓝宝石 OR 金属氧化物) AND 名称,摘要+=(衬底 OR 外延 OR 晶片 OR 单晶 OR 晶圆 OR 晶元 OR 基底 OR 基片 OR 硅片 OR 基板 OR 晶棒 OR 晶片) AND 名称=(方法 OR 工艺) OR 名称=(引线框 OR 引线基架) AND (分类号=('H01L23/495%' OR 'C23C22/63%' OR 'H01L21/60%') OR 申请（专利权）人=(深南 OR 康强 OR 龙华 OR 住友 OR 矿业 OR 日立电线 OR 三井 OR 三星 OR 先进半导体)) OR 名称=((封装 OR 陶瓷 OR 玻璃 OR 树脂 OR 陶瓷 OR AIN OR 复合 OR HTCC OR LTCC OR TFC OR DBC OR DPC OR HTCC OR LTCC OR TFC OR DBC OR DPC) AND (基板 OR 电路板)) AND (分类号=('H01L21/48%' OR 'H01L23/495%' OR 'H01L23/48%') OR 名称=(制造 OR 制备 OR 制作 OR 生产 OR 工艺 OR 加工 OR 半导体 OR 集成电路 OR 结构 设计 OR 形成) AND 分类号=('H01L23%' OR 'H01L21%') OR 申请（专利权）人=(UMTC OR Ibiden OR SEMCO OR Kinsus OR 南亚 OR 深南 OR 兴森 OR 越亚 OR 日月光 OR 景硕 OR 神钢)) OR 名称=((陶瓷 OR TFC OR TPC OR DBC OR DPC OR AMB OR LAM) AND (基板 OR 电路板)) AND (分类号=('H01L21/48%' OR 'H01L23/495%' OR 'H01L23/48%') OR 名称=(制造 OR 制备 OR 制作 OR 生产 OR 工艺 OR 加工 OR 半导体 OR 集成电路 OR 结构 OR 设计 OR 形成) AND 分类号=('H01L23%' OR 'H01L21%') OR 申请（专利权）人=(UMTC OR Ibiden OR SEMCO OR Kinsus OR 南亚 OR 深南 OR 兴森 OR 越亚 OR 日月光 OR 景硕 OR 神钢)) OR 申请（专利权）人=(田中 OR 日铁住金 OR 住友 OR TANAKA OR 日鉄ケミカル OR NIPPON OR 贺利氏 OR 一诺 OR 招金励福 OR 铭凯益 OR 拓自达 OR MKE OR 万生 OR タツタ電線株式会社) AND 名称=((键合) AND (线 OR 丝)) NOT 名称=(装置 OR 设备 OR 检测器 OR 容器 OR 器 OR 工具 OR 夹 OR TOOL OR 盒 OR 键合方法 OR 焊线机 OR 壳 OR 键合方法 OR 单元) OR 名称=(键合线 OR 键合丝 OR 键合银线 OR 键合金线 OR 键合银丝 OR 键合金丝 OR 键合铜线 OR 键合引线 OR 键合铝丝) NOT 名称=(装置 OR 设备 检测器 OR 容器 OR 器 OR 工具 OR 夹 OR TOOL OR 盒 OR 键合方法 OR 焊线机 OR 壳 OR 键合方法 OR 单元) OR 名称,摘要+=(封装 OR 包封 OR 塑封) AND 名称,摘要+=(芯片 OR 集成电路 OR 半导体 OR 微电子) AND 名称,摘要+=(保护) AND 主分类号='C%' AND 名称=(环氧 OR 高分子 OR 树脂 OR 塑料 OR 陶瓷 OR 金属 OR 聚合物) OR 主分类号='C08L63/%' AND 名称,摘要+=(芯片 OR 集成电路 OR 半导体 OR 微电子) AND 名称,摘要+=(封装 OR 包封 OR 塑封) OR 主分类号=('C09J%' OR 'C08L%') AND 名称,摘要+=(封装 OR 包封 OR 塑封) AND 名称,摘要+=(芯片 OR 集成电路 OR 半导体 OR 'IC' OR 微电子) AND 名称=(胶 OR 粘合剂 OR 黏合剂 OR 粘合 OR 黏合 OR 粘结) ) or ( 名称=((CMP OR chemical mechanical polishing) AND (liquid OR Composition OR pad)) OR 名称=('Chemical Mechanical Polishing' OR 'Polishing Pad' OR 'polishing cushion' OR 'coordinate mark' OR 'dressing disk') AND 名称,摘要+=(wafer OR 'integrated circuit' OR semiconductor OR chip) OR 名称=('Chemical Mechanical Polishing' OR 'Polishing Pad' OR 'polishing cushion' OR 'coordinate mark' OR 'dressing disk') AND 名称,摘要+=(wafer OR 'integrated circuit' OR semiconductor OR chip OR circuit AND manufacturing) AND 分类号=('C09K3/14%' OR 'C09G1/02%' OR 'B24B37/24%' OR 'B24B37/20%') OR 名称=(Sputtering AND (Platinum OR Ruthenium OR Aluminum OR Titanium OR Cobalt OR Nickel OR Tantalum OR Copper OR Gold OR Silver OR Alloy) AND target OR 'Sputtering target material' OR 'Sputtering targets material') OR 申请（专利权）人=('JX NIPPON' OR Honeywell OR TOSOH OR PREX OR 'MITSUBISHI MATERIALS') AND 名称=('target material' OR 'Sputtering target' OR 'Sputtering targets') OR (名称=(abrasive liquid OR grinding fluid OR 'Grinding composition' OR 'abrasive composition') AND 名称,摘要+=(wafer OR 'integrated circuit' OR semiconductor OR chip) OR 申请（专利权）人=(Cabot OR Nalco OR Rodel OR DuPont OR Grace OR Akzol Nobel OR Bayer OR Wacker OR Fujimi OR Fujifilm OR Nissan Chemical OR Fuso) AND 名称=(abrasive liquid OR grinding fluid OR 'Grinding composition' OR 'abrasive composition')) NOT 名称=(device OR apparatus OR equipment) OR ((((名称=(('si' OR SOI) AND (Substrate OR wafer OR 'single crystal' OR silicon OR 'Crystal bar' OR semiconductor) AND (Preparation OR Manufacturing OR Production OR Process OR Processing OR Growth OR Formation))) AND 分类号=('C30B29/06%' OR 'C30B25/02%' OR 'H01L21/205%' OR 'C30B23/00%' OR 'H01L21/20%' OR 'H01L21/02%')) OR 申请（专利权）人=(SUMCO OR Siltronic OR SK OR Shin-Etsu OR Shin Etsu) AND 名称=('si' OR SOI) AND 主分类号=('H01L%' OR 'C30B%')) NOT 名称,摘要+=(Polycrystalline OR solar OR 'silicon carbide' OR SIC OR furnace OR equipment OR device)) OR 名称=((GaAs OR 'Gallium arsenide') AND (wafer OR 'single crystal' OR silicon OR 'Crystal bar' OR semiconductor)) AND (名称=(Preparation OR Manufacturing OR Production OR Process OR Processing OR Growth OR Formation) OR 分类号=('C30B29/42%')) OR (名称=((GaN OR 'Gallium nitride') AND (半导体 OR wafer OR 'single crystal' OR silicon OR 'Crystal bar' OR semiconductor)) AND (名称=(Preparation OR Manufacturing OR Production OR Process OR Processing OR Growth OR Formation) OR 分类号=('C30B29/38%')) OR 申请（专利权）人=(HANGZHOU SILAN MICROELECTRONICS OR NANOWIN OR SINO NITRIDE OR enKris) AND 名称=(GaN OR Gallium nitride)) OR (名称=((SiC OR 'Silicon carbide'OR '炭化けい素') AND (wafer OR 'single crystal' OR silicon OR 'Crystal bar' OR semiconductor)) AND (名称=(Preparation OR Manufacturing OR Production OR Process OR Processing OR Growth OR Formation) OR 分类号=('C30B29/38%')) OR 申请（专利权）人=(Norstel OR SiCrystal OR DowCorning OR Infineon) AND 名称=(SiC OR 'Silicon carbide')) OR (((名称=(photoresist) AND 分类号=('G03F7/%' OR 'G03C1/%')) OR 名称=(photoresist) AND 分类号=('G03F7/004%' OR 'G03C1/492%') OR 申请（专利权）人=(JSR OR TOKYO OR HAAS ELECTRONICS OR SUMITOMO CHEMICAL OR 'Shin-Etsu' OR 'Shin Etsu') AND 名称=(photoresist) AND 分类号=('G03F7/%' OR 'G03C1/%'))) NOT 名称=(Remove OR stripping OR Removing OR device OR apparatus OR equipment OR coating) OR ((名称=('Mask Reticle' OR Photomask OR 'Photo mask')) AND (名称=(Base plate OR structure OR pattern OR plate making OR design OR formation OR layout OR manufacture OR preparation OR manufacture OR production OR process OR processing)) AND 分类号=('G03F1/%' OR 'H01L21/027%' OR 'G03F7/%') OR 名称=((reticle) AND (Base plate OR structure OR pattern OR plate making OR design OR formation OR layout OR manufacture OR preparation OR manufacture OR production OR process OR processing)) AND 分类号=('H01L21/027%' OR 'G03F1/00%' OR 'G03F7/20%' OR 'G03F7/00%') OR 名称=('Mask Reticle' OR Photomask OR 'Photo mask') AND 申请（专利权）人=(LG OR DNP OR Toppan OR SHASHIN KAGAKU)) OR (名称=((High purity OR Ultra pure OR Electronic grade OR Ultra clean) AND (Sulfuric acid OR Ammonia OR Hydrogen oxide OR Nitric acid OR Acetic acid OR Hydrochloric acid OR Nitric acid OR Hydrogen oxide OR Hydrogen peroxide OR Hydrofluoric acid OR Ammonium oxide OR Acetone OR Ammonium hydroxide OR Ammonium fluoride OR Potassium hydroxide OR HCl OR CuSO4 OR HNO3 OR NH3·H2O OR phosphoric acid OR Acetic acid OR oxalic acid OR sodium hydroxide OR NaOH OR KOH OR Potassium hydroxide OR tetramethyl ammonium hydroxide OR methanol OR ethanol OR propanol OR acetone OR butanone OR Alcohol OR Ketones OR H2O2)) AND 分类号=('C01B%' OR 'C01C%' OR 'C07C%')) AND 名称,摘要,权利要求书,说明书+=(wafer OR 'integrated circuit' OR semiconductor OR chip OR microelectronics) OR 名称=('Photoresist developer' OR stripper OR diluent OR Detergent OR Etching Solution) AND 名称,摘要+=(Photoresist OR wafer OR 'integrated circuit' OR semiconductor OR chip OR microelectronics) OR (名称=(N2 OR O2 OR H2 OR He OR BCl3 OR BF3 OR PF3 OR AsH3 OR SF6 OR CF4 OR HCl OR CH3F OR NF3 OR CO2 OR C2F6 OR C3F8 OR C4F8 OR CHF3 OR CH2F2 OR CH3F OR ClF3 OR HBr OR HCl OR HF OR C2ClF5 OR CO2 OR CO2 OR NITROGEN OR OXYGEN OR HYDROGEN OR HELIUM OR 'BORON TRICHLORIDE' OR 'BORON TRIFLUORIDE' OR 'PHOSPHORUS TRIFLUORIDE' OR 'HYDROGEN ARSENIDE' OR 'SULFUR HEXAFLUORIDE' OR 'CARBON TETRAFLUORIDE' OR 'HYDROGEN CHLORIDE' OR FLUOROMETHANE OR 'NITROGEN FLUORIDE' OR 'CARBON MONOXIDE' OR 'CARBON DIOXIDE' OR HEXAFLUOROETHANE OR PERFLUOROPROPANE OR FLUOROCYCLOBUTANE OR TRIFLUOROMETHANE OR DIFLUOROMETHANE OR FLUOROMETHANE OR CHLORINE OR 'CHLORINE TRIFLUORIDE' OR 'HYDROGEN BROMIDE' OR 'HYDROGEN CHLORIDE' OR 'HYDROGEN FLUORIDE' OR 'PENTAFLUORO MONOCHLORIDE ETHANE' OR 'CARBON DIOXIDE' OR AMMONIA OR 'NITRIC OXIDE')) AND (名称=( Production OR preparation OR purification)) AND (名称=(Method OR process)) AND (名称,摘要+=(wafer OR 'integrated circuit' OR semiconductor OR chip OR microelectronics)) OR (名称=(GAS) AND 名称=(Electronic grade OR high purity)) AND 名称,摘要+=(Method OR process) OR 名称=((sapphire OR Metal Oxide) AND (Substrate OR wafer OR 'single crystal' OR silicon OR 'Crystal bar' OR Epitaxial OR Epitaxy OR monocrystal) AND (Preparation OR Manufacturing OR Production OR Process OR Processing OR Growth OR Formation)) NOT 名称=(device OR apparatus OR equipment OR crucible) OR 名称=(sapphire OR Metal Oxide) AND 名称,摘要+=(Substrate OR wafer OR 'single crystal' OR silicon OR 'Crystal bar' OR Epitaxial OR Epitaxy OR monocrystal) AND 名称=(Method) OR 名称=(引线框 OR Leadframe OR 引线基架) AND (分类号=('H01L23/495%' OR 'C23C22/63%' OR 'H01L21/60%') OR 申请（专利权）人=(深南 OR 康强 OR 龙华 OR 住友 OR 矿业 OR 日立电线 OR 三井 OR 三星 OR 先进半导体 OR FLEC OR supplier OR sumitomo OR mitsui OR Samsung OR hitachi cable OR shinko OR possell OR asm OR dai nippo)) OR 名称=((封装 OR 陶瓷 OR 玻璃 OR 树脂 OR 陶瓷 OR AIN OR 复合 OR HTCC OR LTCC OR TFC OR DBC OR DPC OR HTCC OR LTCC OR TFC OR DBC OR DPC OR Encapsulated OR ceramic OR glass OR resin) AND (基板 OR substrate OR 电路板)) AND (分类号=('H01L21/48%' OR 'H01L23/495%' OR 'H01L23/48%') OR 名称=(制造 OR 制备 OR 制作 OR 生产 OR 工艺 OR 加工 OR 半导体 OR 集成电路 OR 结构 设计 OR 形成 OR Manufacturing OR preparation OR production OR process OR processing OR semiconductor OR integrated circuit OR structure OR design OR formation) AND 分类号=('H01L23%' OR 'H01L21%') OR 申请（专利权）人=(UMTC OR Ibiden OR SEMCO OR Kinsus OR 南亚 OR 深南 OR 兴森 OR 越亚 OR 日月光 OR 景硕 OR 神钢 OR shinko OR simmtech OR daeduck OR Kyocera OR innotech)) OR 名称=((陶瓷 OR TFC OR TPC OR DBC OR DPC OR AMB OR LAM) AND (基板 OR substrate OR 电路板)) AND (分类号=('H01L21/48%' OR 'H01L23/495%' OR 'H01L23/48%') OR 名称=(制造 OR 制备 OR 制作 OR 生产 OR 工艺 OR 加工 OR 半导体 OR 集成电路 OR 结构 OR 设计 OR 形成 OR Manufacturing OR preparation OR production OR process OR processing OR semiconductor OR integrated circuit OR structure OR design OR formation) AND 分类号=('H01L23%' OR 'H01L21%') OR 申请（专利权）人=(UMTC OR Ibiden OR SEMCO OR Kinsus OR 南亚 OR 深南 OR 兴森 OR 越亚 OR 日月光 OR 景硕 OR 神钢 OR shinko OR simmtech OR daeduck OR Kyocera OR innotech)) OR 申请（专利权）人=(田中 OR 日铁住金 OR 住友 OR TANAKA OR 日鉄ケミカル OR NIPPON OR 贺利氏 OR 一诺 OR 招金励福 OR 铭凯益 OR 拓自达 OR MKE OR 万生 OR タツタ電線株式会社) AND 名称=((键合 OR BOND%) AND (线 OR 丝 OR wire)) NOT 名称=(装置 OR 设备 OR detector OR 检测器 OR 容器 OR 器 OR Device OR equipment OR apparatus OR packag% OR 工具 OR 夹 OR TOOL OR 盒 OR 键合方法 OR 焊线机 OR bonder OR 壳 OR case OR 键合方法 OR 单元 OR nuit) OR 名称=(键合线 OR 键合丝 OR 键合银线 OR 键合金线 OR 键合银丝 OR 键合金丝 OR 'Bond wire' OR 'bonded wire' OR 'bonding wire' OR bondwire OR 键合铜线 OR 键合引线 OR 键合铝丝) NOT 名称=( 装置 OR 设备 OR detector OR 检测器 OR 容器 OR 器 OR Device OR equipment OR apparatus OR packag% OR 工具 OR 夹 OR TOOL OR 盒 OR 键合方法 OR 焊线机 OR bonder OR 壳 OR case OR 键合方法 OR 单元 OR nuit)  OR 名称,摘要+=( 封装 OR 包封 OR 塑封 OR packag% OR Encapsulat%) AND 名称,摘要+=( 芯片 OR 集成电路 OR 半导体 OR Chip OR 'integrated circuit' OR semiconductor OR 'IC' OR 微电子) AND 名称,摘要+=(保护 OR Protect) AND 主分类号='C%' AND 名称=(环氧 OR 高分子 OR 树脂 OR 塑料 OR 陶瓷 OR 金属 OR 聚合物 OR Epoxy OR polymer OR resin OR plastic OR ceramic OR metal) OR 主分类号='C08L63/%' AND 名称,摘要+=(芯片 OR 集成电路 OR 半导体 OR Chip OR 'integrated circuit' OR semiconductor OR 'IC' OR 微电子) AND 名称,摘要+=(封装 OR 包封 OR 塑封 OR packag% OR Encapsulat%) OR 主分类号=('C09J%' OR 'C08L%') AND 名称,摘要+=( 封装 OR 包封 OR 塑封 OR packag%) AND 名称,摘要+=(芯片 OR 集成电路 OR 半导体 OR Chip OR 'integrated circuit' OR semiconductor OR 'IC' OR 微电子) AND 名称=(胶 OR 粘合剂 OR 黏合剂 OR 粘合 OR 黏合 OR adhesive OR 粘结) ))  and 地址=(( (315%浙江省宁波市 or 浙江%宁波 or 宁波%海曙 or 浙江%海曙 or 宁波%江东 or 宁波%江北 or 宁波%北仑 or 浙江%北仑 or 宁波%镇海 or 浙江%镇海 or 宁波%鄞州 or 鄞县 or 浙江%慈溪 or 宁波%慈溪 or 慈溪县 or 浙江%余姚 or 宁波%余姚 or 余姚县 or 浙江%奉化 or 宁波%奉化 or 奉化县 or 浙江%宁海 or 宁波%宁海 or 浙江%象山 or 宁波%象山 or 宁波%国家高新区 or 宁波%科技园区 or 宁波%保税区 or 宁波%大榭开发区 or 宁波%东钱湖旅游度假区)))",
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
