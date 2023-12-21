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
    "Cookie": "JSESSIONID=D28F22D1561B1A1AD3D52B1C6151685C; Hm_lvt_1067a6b069a094a18ed1330087b6bbd1=1697612846; searchcol=%u5730%u5740; Hm_lpvt_1067a6b069a094a18ed1330087b6bbd1=1697613196",
    "Dnt": "1",
    "Host": "chinaip.cnipa.gov.cn",
    "Origin": "http://chinaip.cnipa.gov.cn",
    "Referer": "http://chinaip.cnipa.gov.cn/search!doOverviewSearch.action",
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
    results.to_sql("ct_cnipa_sj", con=engin, index=False, if_exists='append')


if __name__ == '__main__':

    for i in range(84, 116):
        data = {
            "wgViewmodle": "",
            "strWhere": " ((( 名称=((射频前端 OR 'RFFE' OR 'rf front-end' OR 'rf front end' OR 高频前端) AND (芯片 OR 电路 OR Chip OR circuit)) OR (名称=((射频前端 OR RF前端 OR 'Radio frequency front end' OR 'RFFE' OR 'RF frontend' OR 'radio frequency frontend' OR 'RF front end' OR 射频功率放大 OR RF功率放大) AND (模组 OR 模块 OR 电路 OR module OR circuit OR 架构 OR architecture) OR 'Front end module') OR 名称=(射频 AND 前端 OR RF AND 前端 OR 射频模组 OR 射频模块 OR 射频装置 OR RF模组 OR RF模块 OR ('Radio frequency' OR 'RF') AND ('front end' OR frontend) OR 'Radio frequency' AND module OR 高频模块) AND 名称,摘要+=(功率放大 OR 'PA' OR 'power amplifier' OR 低噪声放大 OR 'LNA' OR 'LNAs' OR low noise amplif%) NOT 名称=(amplif% OR 功率放大 OR 低噪声放大) OR 名称=(前端模块 OR 'Front end module' OR 'FEM' OR 前端架构 OR 'Front end architecture') AND 名称,摘要+=(射频 OR 'Radio frequency' OR 'RF')) AND 分类号='H%' OR (名称=(功率放大 OR 'Power Amplifier' OR 功放 OR PA OR 'Power Amplifiers' OR 'Power Amplification') AND 分类号='H03F%' OR 名称=(功率放大器 OR 功率放大电路 OR 功率放大装置)) AND 名称,摘要,权利要求书,说明书+=(射频 OR 'RF' OR 'Radio frequency' OR 移动通信 OR 手机 OR 无线电话 OR 'Mobile Communications' OR 'Mobile Communication' OR 'mobile phone' OR 'wireless telephone') OR ((名称=(放大器 OR 放大电路 OR 放大装置 OR amplifier%) AND 名称,摘要+=('low noise' OR 'low-noise' OR 'LNA' OR 'LNAs' OR 低噪声 OR 低噪音) OR 名称=('LNA' OR 'LNAs') AND 名称,摘要+=('low noise amplif%' OR 低噪 AND (放大器 OR 放大电路 OR 放大装置))) AND 名称,摘要,权利要求书,说明书+=(射频 OR 'RF' OR 'Radio frequency' OR 移动通信 OR 手机 OR 无线电话 OR 'Mobile Communications' OR 'Mobile Communication' OR 'mobile phone' OR 'wireless telephone')) NOT (名称=功率放大 OR 名称,摘要+=LDA) OR (名称=(射频 AND 开关 OR RF开关 OR 'RF 开关' OR 'Radio frequency' AND switch% OR 'RF switch' OR 'RF switches' OR radiofrequency switch%) OR 名称=(开关) AND 名称,摘要+=(射频开关 OR 'RF 开关' OR radiofrequency switch% OR 'Radio frequency' AND switch% OR 射频电路) AND 分类号=('H03K17/%' or 'H04B1/%' or 'H01P1/%')) NOT 名称=(天线 OR antenna) OR (名称=(滤波器 OR filter%) AND 分类号=('H03H9/%' OR 'H03H3/%' or 'H01L41%' OR 'H03H7/01%' OR 'H03H7/03%' OR 'H03H7/06%' OR 'H03H7/065%' OR 'H03H7/07%' OR 'H03H7/075%' OR 'H03H7/09%' OR 'H03H7/12%' OR 'H03H7/13%' OR 'H01P1/%') OR 名称=(滤波器 OR wave filter%) AND 分类号='H01L21/%' OR 名称=(滤波器 OR filter%) AND 主分类号=('H04R17/%' OR 'H03H17/%' OR 'H03H11/%')) OR 名称=((栅极驱动 OR 'Gate drive') AND (电路 OR Circuit)) AND 分类号=('G09G3/36%' OR 'H03K17/687%' OR 'G09G3/20%' OR 'H02M1/08%') OR 名称=(栅极驱动器 OR 栅极驱动器电路 OR 'Gate driver') OR 名称=(LED驱动器 OR LED驱动芯片 OR 发光二极管驱动芯片 OR 发光二极管驱动器 OR LED驱动电路 OR LED驱动IC OR LED驱动电路 OR LED驱动芯片 OR 'LED Driver' OR 'light emitting diode Driver') OR 名称=((LED OR 发光二极管 OR 'light emitting diode Driver') AND (驱动 OR Driver OR Drive OR Driving) AND (电路 OR 芯片 OR circuit OR chip)) AND 分类号=('H05B44%' OR 'H05B37%' OR 'H05B33%' OR 'H05B45%' OR 'G09G3%' OR 'H01L33%') OR (名称=(马达驱动器 OR 马达驱动芯片 OR 马达驱动电路 OR 马达驱动IC OR 电机驱动器 OR 电机驱动芯片 OR 电机驱动电路) OR 名称=((电机 OR 马达 OR Motor) AND (driven OR drive OR driving OR driver) AND (电路 OR circuit OR chip))) AND 主分类号=('H02P6%' OR 'H02P8%' OR 'H02P7%' OR 'H02P27%' OR 'H02P5%' OR 'H02P29%' OR 'H02P25%' OR 'H02P1%' OR 'H02H7%' OR 'H02N2%' OR 'H02M7%' OR 'H02P21%' OR 'H02P23%' OR 'H02P3%') OR 名称=((LCD OR 液晶显示 OR 'Liquid Crystal Display') AND (驱动 OR Driver OR Drive OR Driving) AND (电路 OR 芯片 OR circuit OR chip)) AND 分类号=('G09G3/36%' OR 'G02F1/133%' OR 'G09G3/18%' OR 'G09G3/20%' OR 'G09G5/00%') OR 名称=(LCD驱动器 OR 液晶显示驱动器 OR 液晶显示屏驱动器 OR LCD驱动电路 OR 液晶显示驱动电路 OR 液晶显示屏驱动电路 OR 液晶驱动电路) OR 名称=(驱动器 OR 驱动电路 OR 放大器 OR 放大电路 OR  (drive OR  driving) AND (circuit or CHIP) OR Driver or amplifier OR amplify AND (circuit or CHIP)) AND 名称,摘要+=(音频 OR 万能声卡 OR Audio) AND 主分类号=('H03F%' OR 'H03G%') OR 申请（专利权）人=(STMicroelectronics OR Texas OR Infineon OR Analog OR NXP) AND 名称=(驱动器 OR 驱动电路 OR 放大器 OR 放大电路 OR Driver OR (drive OR driving) AND (circuit OR CHIP) OR amplifier OR amplify AND (circuit OR CHIP)) AND 名称,摘要,权利要求书+=(音频 OR 万能声卡 OR Audio) OR 名称=(驱动器 OR 驱动电路 OR (drive OR driving) AND (circuit OR CHIP) OR Driver) AND (名称,摘要+=(视频 OR video) OR 名称=(显示 OR display)) AND 主分类号=('H04N%' OR 'G09G%') OR 名称=((开关稳压 OR 'Switching regulator' OR 'Switching regulat%') AND (电路 OR 芯片 OR circuit  OR chip)) AND 主分类号=('H02M3%' OR 'G05F1%' OR 'H02H9%' OR 'H02M7%') OR 名称=(开关稳压器 OR 'switching regulator' OR 开关稳压电路) AND 分类号=('H02M3%' OR 'G05F1%' OR 'H02H9%' OR 'H02M7%') OR 名称=(('DC/DC' OR '直流/直流' OR '直流-直流' OR 'DC-DC') AND (转换 OR convert OR 变换) AND (电路 OR circuit OR CHIP)) AND 主分类号=('H02M%' OR 'G05F1%' OR 'H02J%') OR 名称=('直流/直流转换' OR '直流-直流电压转换' OR 'DC/DC转换器' OR 'DC/DC转换电路' OR 'dc/dc converter') OR 名称=(('AC/DC' OR '交流/直流' OR '交流-直流' OR 'AC-DC' OR 交流 AND 直流) AND (转换 OR convert) AND (电路 OR circuit OR CHIP)) AND 主分类号=('H02M%' OR 'H02J%') OR 名称=('交流/直流转换' OR 交直流转换 OR 'AC/DC转换器' OR 'ac/dc转换电路' OR 'Ac/dc converter' OR 交流直流转换) OR (名称=((线性稳压 OR linear) AND (稳压 OR stabilizer OR Regulator OR Regulat%)) AND 主分类号=('H02M3%' OR 'G05F%' OR 'H03F3/45%') OR 名称=(线性稳压器 OR 'Linear Regulator' OR 'LDO' OR 线性稳压电路 OR 'linear stabilizer')) NOT 名称=(非线性 OR 'Non-linear' OR Halblinearer OR semilinear) OR 名称=(保护器 OR Protector OR (保护 OR Protect%) AND (电路 OR circuit OR CHIP)) AND 分类号=('H02H3%' OR 'H02H9%' OR 'H02H7%') AND 名称,摘要+=(过流 OR 过压 OR 过载 OR 过电压 OR 过电流 OR overvoltage OR Overcurrent) OR 分类号=('H02H3%' OR 'H02H9%' OR 'H02H7%') AND 名称=(保护器 OR Protector) AND 名称,摘要+=(过流 OR 过压 OR 过载 OR 过电压 OR 过电流 OR overvoltage OR Overcurrent) OR (名称=(放大器 OR 放大电路 OR 运放电路 OR amplifier OR amplif%) AND 名称,摘要+=(运算放大 OR 'Operational amplifier') AND 分类号=('H03F%' OR 'H03G%') OR 名称=(运算放大器 OR 运算放大电路 OR 运放电路 OR 'Operational amplifier' )) AND 分类号=('H03F%' OR 'H03G%') OR 名称=(放大 OR amplifier) AND 名称=(仪器 OR 仪表 OR instrumentation OR Instrumental) AND 分类号=('H03F%' OR 'H03G%') OR 申请（专利权）人=(德州仪器 OR 国家半导体 OR 美国模拟器件 OR 凌力尔特 OR MaximIntegrated) AND 名称=(放大 OR 'INO' OR amplif%) AND 名称,摘要,权利要求书+=(仪表 OR instrumentation) OR 名称=(差分放大器 OR 'differential amplifier' OR 'difference amplifier' OR 差动放大器 OR 差放) AND 分类号=('H03F%' OR 'H03G%') OR 名称=(放大 OR amplify%) AND 主分类号='H03F3/45%' OR 名称=(比较器 OR 比较电路 OR comparator) AND 主分类号=('H03K%' OR 'G06F7/%' OR 'G01R19%' OR 'H03F3%') OR (名称=(模拟开关 OR 'Analog switch' OR 模拟CMOS开关 OR 数据选择器 OR 数字开关) OR 名称=('SPDT' OR 'Single-Pole Double-Throw' OR 'Single Pole Double Throw') AND (开关) OR 名称=(开关 OR switch ) AND 名称,摘要+=(晶体管 OR Transistor)) AND 分类号='H03K17/%' OR 名称=(接口电路 OR 'interface circuit' OR 'Interfacing circuit')  AND 分类号=('H03%' OR 'H04%') NOT 名称=(封装 OR 制造 OR 制备 OR 制作 OR 封测 OR 测试 OR 系统 OR 生产 OR 装置 OR 设备 OR Packag% OR Manufactur% OR Preparation OR Sealing OR Test OR System OR Production OR Device OR Equipment) OR 名称=(时钟发生器 OR 'clock generator' OR 'Clocked generator') OR 名称=((时钟发生 OR 'clock generator' OR 'Clocked generator') AND (电路 OR circuit)) AND 分类号=('H03K3%' OR 'H03K5%' OR 'H03L7%' OR 'G06F1%' OR 'H04L7%') OR 名称=(时钟缓冲器 OR 'Clock Buffer' OR 'Clocked buffer') OR 名称=((时钟缓冲 OR 'Clock Buffer' OR 'Clocked buffer') AND (电路 OR circuit)) AND 分类号=('H03%' OR 'H04%' OR 'G06%' OR 'G11%') OR 名称=(振荡器 OR 振荡电路 OR oscillator) AND 分类号=('H03%' OR 'H04%') NOT 名称=(封装 OR 制造 OR 制备 OR 制作 OR 封测 OR 测试 OR 系统 OR 生产 OR 装置 OR 设备 OR Packag% OR Manufactur% OR Preparation OR Sealing OR Test OR System OR Production OR Device OR Equipment) OR 名称=((模数 OR A/D) AND 转换 OR 'ADC') AND (电路 OR 芯片 OR Chip OR circuit) AND 分类号=('H03%' OR 'H04%') NOT 名称=(封装 OR 制造 OR 制备 OR 制作 OR 封测 OR 测试 OR 系统 OR 生产 OR 装置 OR 设备 OR Packag% OR Manufactur% OR Preparation OR Sealing OR Test OR System OR Production OR Device OR Equipment) OR 名称=(模数转换器 OR Analog AND Digital Converter OR Analog AND digital transducer) OR 名称=((数模 OR D/A) AND 转换 OR 'DAC') AND (电路 OR 芯片 OR Chip OR circuit) AND 分类号=('H03%' OR 'H04%') NOT 名称=(封装 OR 制造 OR 制备 OR 制作 OR 封测 OR 测试 OR 系统 OR 生产 OR 装置 OR 设备 OR Packag% OR Manufactur% OR Preparation OR Sealing OR Test OR System OR Production OR Device OR Equipment) OR 名称=(数模转换器 OR Digital AND analogue Converter OR Digital AND analogue transducer) OR 名称=(交换 AND 芯片 OR Switch AND Chip OR Switching AND Chip) AND 主分类号=('H04L12%' OR 'G06F13%' OR 'H04L29%' OR 'H04L49%') OR (名称=(微处理器 OR 'MPU' OR 'MCU' OR 'Microcontroller Unit' OR 单片机 OR 'Single Chip Microcomputer' OR 'DSP' OR '微型处理器' OR 'Micro Processor' OR 微控制单元 OR Microprocessor OR 'Micro controller' OR '微型计算机' OR microcomputer OR 'digital signal process' OR 'digital signal processor' OR 'digital signal processing' OR 数字信号处理器 OR 中央处理器 OR 'CPU' OR 中央处理单元 OR 微控制器 OR 数字信号处理器 OR 'CPU' OR 'Central Processing Unit' OR 'Central Processing Processor' 嵌入式 AND 处理器 OR FPGA OR 'Field Programmable Gate Array' OR 现场可编程门阵列 OR 现场可编程逻辑门阵列 OR ASIC OR Application Specific Integrated Circuit OR 专用集成电路 OR 图形处理器 OR 'GPU' OR 'Graphics Processing Unit' OR 视觉处理器 OR 显示芯片 OR 绘图芯片 OR 显示主芯片 OR 图形芯片 OR 图形处理芯片 OR 显卡芯片 OR 存储器 OR DRAM OR SRAM OR 'NAND Flash' OR 'Nor Flash' OR 闪存 OR 'RAM' OR 'ROM' OR FPRAM OR EDORAM OR SDRAM OR RDRAM OR SGRAM OR WRAM OR PRAM OR EPRAM OR EEPRAM OR 数据处理器 OR DPU OR 'Data Processing Unit' OR 数据处理芯片 OR データ処理装置 OR 'data processor' OR 相变存储 OR Phase change memory OR PCM OR 阻变存储 OR ReRAM OR RRAM OR resistive random access memory OR FeRAM OR Ferroelectric RAM OR FRAM OR 铁电存储 OR Ferroelectric Random Access Memory OR Magnetoresistive Random Access Memory OR MRAM OR 'Static Random Access Memory' OR 'Dynamic Random Access Memory' OR 掩膜只读存储 OR 'Mask Read Only Memory' OR MROM OR 掩模式只读存储 OR MASK ROM OR 可编程只读存储器 OR 'Programmable Read-Only Memory' OR PROM OR FPROM) AND 主分类号=('G06F%' OR 'H01L21%' OR 'H01L27%' OR 'G05B19%' OR 'H03K19%' OR 'G11C%' OR 'G06F12%' OR 'G06F13%' OR 'H01L21/8242%')) OR 名称=(逻辑电路 OR 逻辑运算电路 OR 逻辑IC OR 门电路 OR 逻辑门 OR 与门 OR 与非门 OR 或非门 OR 异或门 OR 或门 OR 异或非门 OR Logic Gate OR logic circuits OR Logic circuitry OR 缓冲器 or 驱动器 or 触发器 or 锁存器 or 寄存器 OR 数字比较器 or 编码器 or 解码器 or 单稳态 and 谐振荡 or 锁相环 or 分频器 or 总线交换器 or 电压转化 or 总线交换器 or 收发器 and (奇偶校验 or 寄存 or 标准) or 计数器 or 加法器 or 译码器 or 脉冲顺序分配器 or 反相器 OR decoder OR inhalers OR encoder OR trigger OR counter OR buffer OR latch OR inverter OR adder OR Divider OR comparators) AND 分类号=('H03%' or 'G06%') NOT 名称=(可编程 OR Programmable OR 封装 OR 制造 OR 制备 OR 制作 OR 封测 OR 测试 or 系统 OR 生产 or 装置 or 设备) OR 名称=(人工智能处理器 OR 人工智能处理单元 OR artificial intelligence processor ) NOT 名称=(封装 OR 封测 OR 测试 OR packag% OR encapsulat OR TEST) OR (名称=((基带 OR baseband OR base band) AND (芯片 OR 处理器  OR 处理单元 OR 集成电路 OR chip OR processor OR integrated circuit)) OR 名称,摘要+=(基带芯片 OR 基带处理器 OR 基带处理单元 OR 基带集成电路 OR 'baseband  processor' OR 'baseband chip' OR 'base band unit' OR 'base band  processor' OR 'base band chip' OR 'base band integrated circuit') AND 分类号=('H04B7/%' OR 'H04L1/%' OR 'H04L12/%' OR 'H04W72/%')) AND (名称,摘要,权利要求书+=(5G OR 5th-Generation  OR 5th Generation OR 第五代 OR 第5代 OR fifth generation) OR 说明书=(5G OR 5th-Generation  OR 5th Generation OR 第五代 OR 第5代 OR fifth generation)) OR 名称,摘要+=(基带 AND 应用 AND 处理 OR Baseband AND application AND processor) and 分类号=('G06F%' OR 'H03C3/09' OR 'H03L7/185' OR 'H03L7/22' OR 'H03L7/23' OR 'H04B1/38' OR 'H04B1/40%' OR 'H04B1/401' OR 'H04B1/403' OR 'H04B1/44' OR 'H04B1/50' OR 'H04B1/54' OR 'H04B7%' OR 'H04J3/04' OR 'H04L7%') OR (名称=(微处理器 OR 'MPU' OR 'MCU' OR 'Microcontroller Unit' OR 单片机 OR 'Single Chip Microcomputer' OR 'DSP' OR '微型处理器' OR 'Micro Processor' OR 微控制单元 OR Microprocessor OR 'Micro controller' OR '微型计算机' OR microcomputer OR 'digital signal process' OR 'digital signal processor' OR 'digital signal processing' OR 数字信号处理器 OR 中央处理器 OR 'CPU' OR 中央处理单元 OR 微控制器 OR 数字信号处理器 OR 'CPU' OR 'Central Processing Unit' OR 'Central Processing Processor' 嵌入式 AND 处理器 OR FPGA OR 'Field Programmable Gate Array' OR 现场可编程门阵列 OR 现场可编程逻辑门阵列 OR ASIC OR Application Specific Integrated Circuit OR 专用集成电路 OR 图形处理器 OR 'GPU' OR 'Graphics Processing Unit' OR 视觉处理器 OR 显示芯片 OR 绘图芯片 OR 显示主芯片 OR 图形芯片 OR 图形处理芯片 OR 显卡芯片 OR 存储器 OR DRAM OR SRAM OR 'NAND Flash' OR 'Nor Flash' OR 闪存 OR 'RAM' OR 'ROM' OR FPRAM OR EDORAM OR SDRAM OR RDRAM OR SGRAM OR WRAM OR PRAM OR EPRAM OR EEPRAM OR 数据处理器 OR DPU OR 'Data Processing Unit' OR 数据处理芯片 OR データ処理装置 OR 'data processor' OR 相变存储 OR Phase change memory OR PCM OR 阻变存储 OR ReRAM OR RRAM OR  resistive random access memory OR FeRAM OR Ferroelectric RAM OR FRAM OR 铁电存储 OR Ferroelectric Random Access Memory OR Magnetoresistive Random Access Memory OR MRAM OR 'Static Random Access Memory' OR 'Dynamic Random Access Memory' OR 掩膜只读存储 OR 'Mask Read Only Memory' OR MROM OR 掩模式只读存储 OR MASK ROM OR 可编程只读存储器 OR 'Programmable Read-Only Memory' OR PROM OR FPROM ) AND 主分类号=('G06F%' OR 'H01L21%' OR 'H01L27%' OR 'G05B19%' OR 'H03K19%' OR 'G11C%' OR 'G06F12%' OR 'G06F13%' OR 'H01L21%' OR 'H01L27%' OR 'H01L21/8242%' OR 'H01L21/8242%')) OR 名称=(逻辑电路 OR 逻辑运算电路 OR 逻辑IC OR 门电路 OR 逻辑门 OR 与门 OR 与非门 OR 或非门 OR 异或门 OR 或门 OR 异或非门 OR Logic Gate OR logic circuits OR Logic circuitry OR 缓冲器 or 驱动器 or 触发器 or 锁存器 or 寄存器 OR 数字比较器 or 编码器 or 解码器 or 单稳态 and 谐振荡 or 锁相环 or 分频器 or 总线交换器 or 电压转化 or 总线交换器 or 收发器 and (奇偶校验 or 寄存 or 标准) or 计数器 or 加法器 or 译码器 or 脉冲顺序分配器 or 反相器 OR decoder OR inhalers OR encoder OR trigger OR counter OR buffer OR latch OR inverter OR adder OR Divider OR comparators) AND 分类号=('H03%' or 'G06%') NOT 名称=(可编程 OR Programmable OR 封装 OR 制造 OR 制备 OR 制作 OR 封测 OR 测试 or 系统 OR 生产 or 装置 or 设备) OR 名称=(人工智能 AND 处理器 OR 人工智能 AND 处理单元 OR (artificial intelligence OR Artificial Intelligent OR AI) AND (processor OR Unit) OR AI处理器 OR 神经网络处理器 OR 神经网络处理器 OR 神经网络处理单元 OR Neural network Processing Unit OR Neural network Processor ) NOT 名称=(封装 OR 封测 OR 测试 OR packag% OR encapsulat OR TEST) OR 名称,摘要+=(基带 AND 应用 AND 处理 OR Baseband AND application AND processor) and 分类号=('G06F%' OR 'H03C3/09' OR 'H03L7/185' OR 'H03L7/22' OR 'H03L7/23' OR 'H04B1/38' OR 'H04B1/40%' OR 'H04B1/401' OR 'H04B1/403' OR 'H04B1/44' OR 'H04B1/50' OR 'H04B1/54' OR 'H04B7%' OR 'H04J3/04' OR 'H04L7%')  OR (名称=(中央处理器 OR 中央处理单元 OR 'CPU' OR 'Central Processing Unit' OR 'Central Processing Processor' or 'Central processor' OR图形处理器 OR 'GPU' OR 'Graphics Processing Unit' OR 视觉处理器 OR 显示芯片 OR 绘图芯片 OR 显示主芯片 OR 图形芯片 OR 图形处理芯片 OR 显卡芯片 OR DSP OR 'digital signal process' OR 数字信号处理器 OR 'digital signal processor' OR 'digital signal processing' OR 通用处理器 OR general-purpose processor OR General-purpose computing on graphics processing units) AND 主分类号=('G06F%' OR 'H01L21%' OR 'H01L27%' OR 'G05B19%')) OR 名称=(人工智能 AND 处理器 OR 人工智能 AND 处理单元 OR (artificial intelligence OR Artificial Intelligent OR AI) AND (processor OR Unit) OR AI处理器 OR 神经网络处理器  OR 神经网络处理器 OR 神经网络处理单元 OR Neural network Processing Unit OR Neural network Processor) NOT 名称=(封装 OR 封测 OR 测试 OR packag% OR encapsulat OR TEST) OR (名称=('ASIC' OR Application Specific AND Integrated Circuit OR 专用 AND 芯片 OR 专用 AND 集成电路 OR Special purpose AND Circuit OR Special purpose AND chip OR Application Specific AND chip OR specific function AND Circuit  OR pecific function AND chip ) AND 分类号=('G06F/%' OR 'H01L21/%' OR 'H01L23/%' OR 'H01L25/%' OR 'H01L27/%' OR 'H03K/%') OR 申请（专利权）人=(纳芯微 OR 瑞斯康达 OR 谷歌 OR 英特尔 OR 三星 OR Google OR Intel  OR SAMSUNG OR 国际商业 OR INTERNATIONAL BUSINESS MACHINES OR IBM) AND 名称,摘要+=('ASIC' OR Application Specific Integrated Circuit OR 专用芯片 OR 专用集成电路) AND 分类号=('G06F/%' OR 'H01L21/%' OR 'H01L23/%' OR 'H01L25/%' OR 'H01L27/%' OR 'H03K/%')) NOT 名称=(封装 OR 封测 OR Packaging) OR 名称=(((可重构 OR 软件定义 OR reconfigurable) AND (芯片 OR chip OR Circuit))) OR (名称=((基带 OR Baseband) AND (芯片 OR 处理器 OR 解调器 OR chip OR PROCESSOR OR modem)) OR 名称,摘要+=(基带 OR Baseband) AND 分类号=('H04B7/%' OR 'H04L1/%' OR 'H04L12/%' OR 'H04W72/%') AND 名称=(芯片 OR 处理器 OR 解调器 OR chip OR PROCESSOR OR modem) OR 名称,摘要+=(基带芯片 OR 基带处理器 OR 基带解调器 OR Baseband CHIP OR Baseband OR  PROCESSOR OR Baseband modem) AND 申请（专利权）人=(华为 OR 高通 OR 英特尔 OR 三星 OR HUAWEI OR QUALCOMM OR Intel OR SAMSUNG)) AND 名称,摘要,权利要求书+=(5G OR 第五代 OR 第5代) ) or ( 名称=((射频前端 OR 'RFFE' OR 'rf front-end' OR 'rf front end' OR 高频前端) AND (芯片 OR 电路 OR Chip OR circuit)) OR (名称=((射频前端 OR RF前端 OR 'Radio frequency front end' OR 'RFFE' OR 'RF frontend' OR 'radio frequency frontend' OR 'RF front end' OR 射频功率放大 OR RF功率放大) AND (模组 OR 模块 OR 电路 OR module OR circuit OR 架构 OR architecture) OR 'Front end module') OR 名称=(射频 AND 前端 OR RF AND 前端 OR 射频模组 OR 射频模块 OR 射频装置 OR RF模组 OR RF模块 OR ('Radio frequency' OR 'RF') AND ('front end' OR frontend) OR 'Radio frequency' AND module OR 高频模块) AND 名称,摘要+=(功率放大 OR 'PA' OR 'power amplifier' OR 低噪声放大 OR 'LNA' OR 'LNAs' OR low noise amplif%) NOT 名称=(amplif% OR 功率放大 OR 低噪声放大) OR 名称=(前端模块 OR 'Front end module' OR 'FEM' OR 前端架构 OR 'Front end architecture') AND 名称,摘要+=(射频 OR 'Radio frequency' OR 'RF')) AND 分类号='H%' OR (名称=(功率放大 OR 'Power Amplifier' OR 功放 OR PA OR 'Power Amplifiers' OR 'Power Amplification') AND 分类号='H03F%' OR 名称=(功率放大器 OR 功率放大电路 OR 功率放大装置)) AND 名称,摘要,权利要求书,说明书+=(射频 OR 'RF' OR 'Radio frequency' OR 移动通信 OR 手机 OR 无线电话 OR 'Mobile Communications' OR 'Mobile Communication' OR 'mobile phone' OR 'wireless telephone') OR ((名称=(放大器 OR 放大电路 OR 放大装置 OR amplifier%) AND 名称,摘要+=('low noise' OR 'low-noise' OR 'LNA' OR 'LNAs' OR 低噪声 OR 低噪音) OR 名称=('LNA' OR 'LNAs') AND 名称,摘要+=('low noise amplif%' OR 低噪 AND (放大器 OR 放大电路 OR 放大装置))) AND 名称,摘要,权利要求书,说明书+=(射频 OR 'RF' OR 'Radio frequency' OR 移动通信 OR 手机 OR 无线电话 OR 'Mobile Communications' OR 'Mobile Communication' OR 'mobile phone' OR 'wireless telephone')) NOT (名称=功率放大 OR 名称,摘要+=LDA) OR (名称=(射频 AND 开关 OR RF开关 OR 'RF 开关' OR 'Radio frequency' AND switch% OR 'RF switch' OR 'RF switches' OR radiofrequency switch%) OR 名称=(开关) AND 名称,摘要+=(射频开关 OR 'RF 开关' OR radiofrequency switch% OR 'Radio frequency' AND switch% OR 射频电路) AND 分类号=('H03K17/%' or 'H04B1/%' or 'H01P1/%')) NOT 名称=(天线 OR antenna) OR (名称=(滤波器 OR filter%) AND 分类号=('H03H9/%' OR 'H03H3/%' or 'H01L41%' OR 'H03H7/01%' OR 'H03H7/03%' OR 'H03H7/06%' OR 'H03H7/065%' OR 'H03H7/07%' OR 'H03H7/075%' OR 'H03H7/09%' OR 'H03H7/12%' OR 'H03H7/13%' OR 'H01P1/%') OR 名称=(滤波器 OR wave filter%) AND 分类号='H01L21/%' OR 名称=(滤波器 OR filter%) AND 主分类号=('H04R17/%' OR 'H03H17/%' OR 'H03H11/%')) OR 名称=((栅极驱动 OR 'Gate drive') AND (电路 OR Circuit)) AND 分类号=('G09G3/36%' OR 'H03K17/687%' OR 'G09G3/20%' OR 'H02M1/08%') OR 名称=(栅极驱动器 OR 栅极驱动器电路 OR 'Gate driver') OR 名称=(LED驱动器 OR LED驱动芯片 OR 发光二极管驱动芯片 OR 发光二极管驱动器 OR LED驱动电路 OR LED驱动IC OR LED驱动电路 OR LED驱动芯片 OR 'LED Driver' OR 'light emitting diode Driver') OR 名称=((LED OR 发光二极管 OR 'light emitting diode Driver') AND (驱动 OR Driver OR Drive OR Driving) AND (电路 OR 芯片 OR circuit OR chip)) AND 分类号=('H05B44%' OR 'H05B37%' OR 'H05B33%' OR 'H05B45%' OR 'G09G3%' OR 'H01L33%') OR (名称=(马达驱动器 OR 马达驱动芯片 OR 马达驱动电路 OR 马达驱动IC OR 电机驱动器 OR 电机驱动芯片 OR 电机驱动电路) OR 名称=((电机 OR 马达 OR Motor) AND (driven OR drive OR driving OR driver) AND (电路 OR circuit OR chip))) AND 主分类号=('H02P6%' OR 'H02P8%' OR 'H02P7%' OR 'H02P27%' OR 'H02P5%' OR 'H02P29%' OR 'H02P25%' OR 'H02P1%' OR 'H02H7%' OR 'H02N2%' OR 'H02M7%' OR 'H02P21%' OR 'H02P23%' OR 'H02P3%') OR 名称=((LCD OR 液晶显示 OR 'Liquid Crystal Display') AND (驱动 OR Driver OR Drive OR Driving) AND (电路 OR 芯片 OR circuit OR chip)) AND 分类号=('G09G3/36%' OR 'G02F1/133%' OR 'G09G3/18%' OR 'G09G3/20%' OR 'G09G5/00%') OR 名称=(LCD驱动器 OR 液晶显示驱动器 OR 液晶显示屏驱动器 OR LCD驱动电路 OR 液晶显示驱动电路 OR 液晶显示屏驱动电路 OR 液晶驱动电路) OR 名称=(驱动器 OR 驱动电路 OR 放大器 OR 放大电路 OR  (drive OR  driving) AND (circuit or CHIP) OR Driver or amplifier OR amplify AND (circuit or CHIP)) AND 名称,摘要+=(音频 OR 万能声卡 OR Audio) AND 主分类号=('H03F%' OR 'H03G%') OR 申请（专利权）人=(STMicroelectronics OR Texas OR Infineon OR Analog OR NXP) AND 名称=(驱动器 OR 驱动电路 OR 放大器 OR 放大电路 OR Driver OR (drive OR driving) AND (circuit OR CHIP) OR amplifier OR amplify AND (circuit OR CHIP)) AND 名称,摘要,权利要求书+=(音频 OR 万能声卡 OR Audio) OR 名称=(驱动器 OR 驱动电路 OR (drive OR driving) AND (circuit OR CHIP) OR Driver) AND (名称,摘要+=(视频 OR video) OR 名称=(显示 OR display)) AND 主分类号=('H04N%' OR 'G09G%') OR 名称=((开关稳压 OR 'Switching regulator' OR 'Switching regulat%') AND (电路 OR 芯片 OR circuit  OR chip)) AND 主分类号=('H02M3%' OR 'G05F1%' OR 'H02H9%' OR 'H02M7%') OR 名称=(开关稳压器 OR 'switching regulator' OR 开关稳压电路) AND 分类号=('H02M3%' OR 'G05F1%' OR 'H02H9%' OR 'H02M7%') OR 名称=(('DC/DC' OR '直流/直流' OR '直流-直流' OR 'DC-DC') AND (转换 OR convert OR 变换) AND (电路 OR circuit OR CHIP)) AND 主分类号=('H02M%' OR 'G05F1%' OR 'H02J%') OR 名称=('直流/直流转换' OR '直流-直流电压转换' OR 'DC/DC转换器' OR 'DC/DC转换电路' OR 'dc/dc converter') OR 名称=(('AC/DC' OR '交流/直流' OR '交流-直流' OR 'AC-DC' OR 交流 AND 直流) AND (转换 OR convert) AND (电路 OR circuit OR CHIP)) AND 主分类号=('H02M%' OR 'H02J%') OR 名称=('交流/直流转换' OR 交直流转换 OR 'AC/DC转换器' OR 'AC/DC转换电路' OR 'Ac/dc converter' OR 交流直流转换) OR (名称=((线性稳压 OR linear) AND (稳压 OR stabilizer OR Regulator OR Regulat%)) AND 主分类号=('H02M3%' OR 'G05F%' OR 'H03F3/45%') OR 名称=(线性稳压器 OR 'Linear Regulator' OR 'LDO' OR 线性稳压电路 OR 'linear stabilizer')) NOT 名称=(非线性 OR 'Non-linear' OR Halblinearer OR semilinear) OR 名称=(保护器 OR Protector OR (保护 OR Protect%) AND (电路 OR circuit OR CHIP)) AND 分类号=('H02H3%' OR 'H02H9%' OR 'H02H7%') AND 名称,摘要+=(过流 OR 过压 OR 过载 OR 过电压 OR 过电流 OR overvoltage OR Overcurrent) OR 分类号=('H02H3%' OR 'H02H9%' OR 'H02H7%') AND 名称=(保护器 OR Protector) AND 名称,摘要+=(过流 OR 过压 OR 过载 OR 过电压 OR 过电流 OR overvoltage OR Overcurrent) OR (名称=(放大器 OR 放大电路 OR 运放电路 OR amplifier OR amplif%) AND 名称,摘要+=(运算放大 OR 'Operational amplifier') AND 分类号=('H03F%' OR 'H03G%') OR 名称=(运算放大器 OR 运算放大电路 OR 运放电路 OR 'Operational amplifier' )) AND 分类号=('H03F%' OR 'H03G%') OR 名称=(放大 OR amplifier) AND 名称=(仪器 OR 仪表 OR instrumentation OR Instrumental) AND 分类号=('H03F%' OR 'H03G%') OR 申请（专利权）人=(德州仪器 OR 国家半导体 OR 美国模拟器件 OR 凌力尔特 OR MaximIntegrated) AND 名称=(放大 OR 'INO' OR amplif%) AND 名称,摘要,权利要求书+=(仪表 OR instrumentation) OR 名称=(差分放大器 OR 'differential amplifier' OR 'difference amplifier' OR 差动放大器 OR 差放) AND 分类号=('H03F%' OR 'H03G%') OR 名称=(放大 OR amplify%) AND 主分类号='H03F3/45%' OR 名称=(比较器 OR 比较电路 OR comparator) AND 主分类号=('H03K%' OR 'G06F7/%' OR 'G01R19%' OR 'H03F3%') OR (名称=(模拟开关 OR 'Analog switch' OR 模拟CMOS开关 OR 数据选择器 OR 数字开关) OR 名称=('SPDT' OR 'Single-Pole Double-Throw' OR 'Single Pole Double Throw') AND (开关) OR 名称=(开关 OR switch ) AND 名称,摘要+=(晶体管 OR Transistor)) AND 分类号='H03K17/%' OR 名称=(接口电路 OR 'interface circuit' OR 'Interfacing circuit')  AND 分类号=('H03%' OR 'H04%') NOT 名称=(封装 OR 制造 OR 制备 OR 制作 OR 封测 OR 测试 OR 系统 OR 生产 OR 装置 OR 设备 OR Packag% OR Manufactur% OR Preparation OR Sealing OR Test OR System OR Production OR Device OR Equipment) OR 名称=(时钟发生器 OR 'clock generator' OR 'Clocked generator') OR 名称=((时钟发生 OR 'clock generator' OR 'Clocked generator') AND (电路 OR circuit)) AND 分类号=('H03K3%' OR 'H03K5%' OR 'H03L7%' OR 'G06F1%' OR 'H04L7%') OR 名称=(时钟缓冲器 OR 'Clock Buffer' OR 'Clocked buffer') OR 名称=((时钟缓冲 OR 'Clock Buffer' OR 'Clocked buffer') AND (电路 OR circuit)) AND 分类号=('H03%' OR 'H04%' OR 'G06%' OR 'G11%') OR 名称=(振荡器 OR 振荡电路 OR oscillator) AND 分类号=('H03%' OR 'H04%') NOT 名称=(封装 OR 制造 OR 制备 OR 制作 OR 封测 OR 测试 OR 系统 OR 生产 OR 装置 OR 设备 OR Packag% OR Manufactur% OR Preparation OR Sealing OR Test OR System OR Production OR Device OR Equipment) OR 名称=((模数 OR A/D) AND 转换 OR 'ADC') AND (电路 OR 芯片 OR Chip OR circuit) AND 分类号=('H03%' OR 'H04%') NOT 名称=(封装 OR 制造 OR 制备 OR 制作 OR 封测 OR 测试 OR 系统 OR 生产 OR 装置 OR 设备 OR Packag% OR Manufactur% OR Preparation OR Sealing OR Test OR System OR Production OR Device OR Equipment) OR 名称=(模数转换器 OR Analog AND Digital Converter OR Analog AND digital transducer) OR 名称=((数模 OR D/A) AND 转换 OR 'DAC') AND (电路 OR 芯片 OR Chip OR circuit) AND 分类号=('H03%' OR 'H04%') NOT 名称=(封装 OR 制造 OR 制备 OR 制作 OR 封测 OR 测试 OR 系统 OR 生产 OR 装置 OR 设备 OR Packag% OR Manufactur% OR Preparation OR Sealing OR Test OR System OR Production OR Device OR Equipment) OR 名称=(数模转换器 OR Digital AND analogue Converter OR Digital AND analogue transducer) OR 名称=(交换 AND 芯片 OR Switch AND Chip OR Switching AND Chip) AND 主分类号=('H04L12%' OR 'G06F13%' OR 'H04L29%' OR 'H04L49%') OR (名称=(微处理器 OR 'MPU' OR 'MCU' OR 'Microcontroller Unit' OR 单片机 OR 'Single Chip Microcomputer' OR 'DSP' OR '微型处理器' OR 'Micro Processor' OR 微控制单元 OR Microprocessor OR 'Micro controller' OR '微型计算机' OR microcomputer OR 'digital signal process' OR 'digital signal processor' OR 'digital signal processing' OR 数字信号处理器 OR 中央处理器 OR 'CPU' OR 中央处理单元 OR 微控制器 OR 数字信号处理器 OR 'CPU' OR 'Central Processing Unit' OR 'Central Processing Processor' 嵌入式 AND 处理器 OR FPGA OR 'Field Programmable Gate Array' OR 现场可编程门阵列 OR 现场可编程逻辑门阵列 OR ASIC OR Application Specific Integrated Circuit OR 专用集成电路 OR 图形处理器 OR 'GPU' OR 'Graphics Processing Unit' OR 视觉处理器 OR 显示芯片 OR 绘图芯片 OR 显示主芯片 OR 图形芯片 OR 图形处理芯片 OR 显卡芯片 OR 存储器 OR DRAM OR SRAM OR 'NAND Flash' OR 'Nor Flash' OR 闪存 OR 'RAM' OR 'ROM' OR FPRAM OR EDORAM OR SDRAM OR RDRAM OR SGRAM OR WRAM OR PRAM OR EPRAM OR EEPRAM OR 数据处理器 OR DPU OR 'Data Processing Unit' OR 数据处理芯片 OR データ処理装置 OR 'data processor' OR 相变存储 OR Phase change memory OR PCM OR 阻变存储 OR ReRAM OR RRAM OR resistive random access memory OR FeRAM OR Ferroelectric RAM OR FRAM OR 铁电存储 OR Ferroelectric Random Access Memory OR Magnetoresistive Random Access Memory OR MRAM OR 'Static Random Access Memory' OR 'Dynamic Random Access Memory' OR 掩膜只读存储 OR 'Mask Read Only Memory' OR MROM OR 掩模式只读存储 OR MASK ROM OR 可编程只读存储器 OR 'Programmable Read-Only Memory' OR PROM OR FPROM) AND 主分类号=('G06F%' OR 'H01L21%' OR 'H01L27%' OR 'G05B19%' OR 'H03K19%' OR 'G11C%' OR 'G06F12%' OR 'G06F13%' OR 'H01L21/8242%')) OR 名称=(逻辑电路 OR 逻辑运算电路 OR 逻辑IC OR 门电路 OR 逻辑门 OR 与门 OR 与非门 OR 或非门 OR 异或门 OR 或门 OR 异或非门 OR Logic Gate OR logic circuits OR Logic circuitry OR 缓冲器 or 驱动器 or 触发器 or 锁存器 or 寄存器 OR 数字比较器 or 编码器 or 解码器 or 单稳态 and 谐振荡 or 锁相环 or 分频器 or 总线交换器 or 电压转化 or 总线交换器 or 收发器 and (奇偶校验 or 寄存 or 标准) or 计数器 or 加法器 or 译码器 or 脉冲顺序分配器 or 反相器 OR decoder OR inhalers OR encoder OR trigger OR counter OR buffer OR latch OR inverter OR adder OR Divider OR comparators) AND 分类号=('H03%' or 'G06%') NOT 名称=(可编程 OR Programmable OR 封装 OR 制造 OR 制备 OR 制作 OR 封测 OR 测试 or 系统 OR 生产 or 装置 or 设备) OR 名称=(人工智能处理器 OR 人工智能处理单元 OR artificial intelligence processor ) NOT 名称=(封装 OR 封测 OR 测试 OR packag% OR encapsulat OR TEST) OR (名称=((基带 OR baseband OR base band) AND (芯片 OR 处理器  OR 处理单元 OR 集成电路 OR chip OR processor OR integrated circuit)) OR 名称,摘要+=(基带芯片 OR 基带处理器 OR 基带处理单元 OR 基带集成电路 OR 'baseband  processor' OR 'baseband chip' OR 'base band unit' OR 'base band  processor' OR 'base band chip' OR 'base band integrated circuit') AND 分类号=('H04B7/%' OR 'H04L1/%' OR 'H04L12/%' OR 'H04W72/%')) AND (名称,摘要,权利要求书+=(5G OR 5th-Generation  OR 5th Generation OR 第五代 OR 第5代 OR fifth generation) OR 说明书=(5G OR 5th-Generation  OR 5th Generation OR 第五代 OR 第5代 OR fifth generation)) OR 名称,摘要+=(基带 AND 应用 AND 处理 OR Baseband AND application AND processor) and 分类号=('G06F%' OR 'H03C3/09' OR 'H03L7/185' OR 'H03L7/22' OR 'H03L7/23' OR 'H04B1/38' OR 'H04B1/40%' OR 'H04B1/401' OR 'H04B1/403' OR 'H04B1/44' OR 'H04B1/50' OR 'H04B1/54' OR 'H04B7%' OR 'H04J3/04' OR 'H04L7%')  OR (名称=(微处理器 OR 'MPU' OR 'MCU' OR 'Microcontroller Unit' OR 单片机 OR 'Single Chip Microcomputer' OR 'DSP' OR '微型处理器' OR 'Micro Processor' OR 微控制单元 OR Microprocessor OR 'Micro controller' OR '微型计算机' OR microcomputer OR 'digital signal process' OR 'digital signal processor' OR 'digital signal processing' OR 数字信号处理器 OR 中央处理器 OR 'CPU' OR 中央处理单元 OR 微控制器 OR 数字信号处理器 OR 'CPU' OR 'Central Processing Unit' OR 'Central Processing Processor' 嵌入式 AND 处理器 OR FPGA OR 'Field Programmable Gate Array' OR 现场可编程门阵列 OR 现场可编程逻辑门阵列 OR ASIC OR Application Specific Integrated Circuit OR 专用集成电路 OR 图形处理器 OR 'GPU' OR 'Graphics Processing Unit' OR 视觉处理器 OR 显示芯片 OR 绘图芯片 OR 显示主芯片 OR 图形芯片 OR 图形处理芯片 OR 显卡芯片 OR 存储器 OR DRAM OR SRAM OR 'NAND Flash' OR 'Nor Flash' OR 闪存 OR 'RAM' OR 'ROM' OR FPRAM OR EDORAM OR SDRAM OR RDRAM OR SGRAM OR WRAM OR PRAM OR EPRAM OR EEPRAM OR 数据处理器 OR DPU OR 'Data Processing Unit' OR 数据处理芯片 OR データ処理装置 OR 'data processor' OR 相变存储 OR Phase change memory OR PCM OR 阻变存储 OR ReRAM OR RRAM OR  resistive random access memory OR FeRAM OR Ferroelectric RAM OR FRAM OR 铁电存储 OR Ferroelectric Random Access Memory OR Magnetoresistive Random Access Memory OR MRAM OR 'Static Random Access Memory' OR 'Dynamic Random Access Memory' OR 掩膜只读存储 OR 'Mask Read Only Memory' OR MROM OR 掩模式只读存储 OR MASK ROM OR 可编程只读存储器 OR 'Programmable Read-Only Memory' OR PROM OR FPROM ) AND 主分类号=('G06F%' OR 'H01L21%' OR 'H01L27%' OR 'G05B19%' OR 'H03K19%' OR 'G11C%' OR 'G06F12%' OR 'G06F13%' OR 'H01L21%' OR 'H01L27%' OR 'H01L21/8242%' OR 'H01L21/8242%')) OR 名称=(逻辑电路 OR 逻辑运算电路 OR 逻辑IC OR 门电路 OR 逻辑门 OR 与门 OR 与非门 OR 或非门 OR 异或门 OR 或门 OR 异或非门 OR Logic Gate OR logic circuits OR Logic circuitry OR 缓冲器 or 驱动器 or 触发器 or 锁存器 or 寄存器 OR 数字比较器 or 编码器 or 解码器 or 单稳态 and 谐振荡 or 锁相环 or 分频器 or 总线交换器 or 电压转化 or 总线交换器 or 收发器 and (奇偶校验 or 寄存 or 标准) or 计数器 or 加法器 or 译码器 or 脉冲顺序分配器 or 反相器 OR decoder OR inhalers OR encoder OR trigger OR counter OR buffer OR latch OR inverter OR adder OR Divider OR comparators) AND 分类号=('H03%' or 'G06%') NOT 名称=(可编程 OR Programmable OR 封装 OR 制造 OR 制备 OR 制作 OR 封测 OR 测试 or 系统 OR 生产 or 装置 or 设备) OR 名称=(人工智能 AND 处理器 OR 人工智能 AND 处理单元 OR (artificial intelligence OR Artificial Intelligent OR AI) AND (processor OR Unit) OR AI处理器 OR 神经网络处理器 OR 神经网络处理器 OR 神经网络处理单元 OR Neural network Processing Unit OR Neural network Processor ) NOT 名称=(封装 OR 封测 OR 测试 OR packag% OR encapsulat OR TEST) OR 名称,摘要+=(基带 AND 应用 AND 处理 OR Baseband AND application AND processor) and 分类号=('G06F%' OR 'H03C3/09' OR 'H03L7/185' OR 'H03L7/22' OR 'H03L7/23' OR 'H04B1/38' OR 'H04B1/40%' OR 'H04B1/401' OR 'H04B1/403' OR 'H04B1/44' OR 'H04B1/50' OR 'H04B1/54' OR 'H04B7%' OR 'H04J3/04' OR 'H04L7%')  OR (名称=(中央处理器 OR 中央处理单元 OR 'CPU' OR 'Central Processing Unit' OR 'Central Processing Processor' or 'Central processor' OR图形处理器 OR 'GPU' OR 'Graphics Processing Unit' OR 视觉处理器 OR 显示芯片 OR 绘图芯片 OR 显示主芯片 OR 图形芯片 OR 图形处理芯片 OR 显卡芯片 OR DSP OR 'digital signal process' OR 数字信号处理器 OR 'digital signal processor' OR 'digital signal processing' OR 通用处理器 OR general-purpose processor OR General-purpose computing on graphics processing units) AND 主分类号=('G06F%' OR 'H01L21%' OR 'H01L27%' OR 'G05B19%')) OR 名称=(人工智能 AND 处理器 OR 人工智能 AND 处理单元 OR (artificial intelligence OR Artificial Intelligent OR AI) AND (processor OR Unit) OR AI处理器 OR 神经网络处理器  OR 神经网络处理器 OR 神经网络处理单元 OR Neural network Processing Unit OR Neural network Processor) NOT 名称=(封装 OR 封测 OR 测试 OR packag% OR encapsulat OR TEST) OR (名称=('ASIC' OR Application Specific AND Integrated Circuit OR 专用 AND 芯片 OR 专用 AND 集成电路 OR Special purpose AND Circuit OR Special purpose AND chip OR Application Specific AND chip OR specific function AND Circuit  OR pecific function AND chip ) AND 分类号=('G06F/%' OR 'H01L21/%' OR 'H01L23/%' OR 'H01L25/%' OR 'H01L27/%' OR 'H03K/%') OR 申请（专利权）人=(纳芯微 OR 瑞斯康达 OR 谷歌 OR 英特尔 OR 三星 OR Google OR Intel  OR SAMSUNG OR 国际商业 OR INTERNATIONAL BUSINESS MACHINES OR IBM) AND 名称,摘要+=('ASIC' OR Application Specific Integrated Circuit OR 专用芯片 OR 专用集成电路) AND 分类号=('G06F/%' OR 'H01L21/%' OR 'H01L23/%' OR 'H01L25/%' OR 'H01L27/%' OR 'H03K/%')) NOT 名称=(封装 OR 封测 OR Packaging) OR 名称=(((可重构 OR 软件定义 OR reconfigurable) AND (芯片 OR chip OR Circuit))) OR (名称=((基带 OR Baseband) AND (芯片 OR 处理器 OR 解调器 OR chip OR PROCESSOR OR modem)) OR 名称,摘要+=(基带 OR Baseband) AND 分类号=('H04B7/%' OR 'H04L1/%' OR 'H04L12/%' OR 'H04W72/%') AND 名称=(芯片 OR 处理器 OR 解调器 OR chip OR PROCESSOR OR modem) OR 名称,摘要+=(基带芯片 OR 基带处理器 OR 基带解调器 OR Baseband CHIP OR Baseband OR  PROCESSOR OR Baseband modem) AND 申请（专利权）人=(华为 OR 高通 OR 英特尔 OR 三星 OR HUAWEI OR QUALCOMM OR Intel OR SAMSUNG)) AND 名称,摘要,权利要求书+=(5G OR 第五代 OR 第5代) ))  and 地址=(( (315%浙江省宁波市 or 浙江%宁波 or 宁波%海曙 or 浙江%海曙 or 宁波%江东 or 宁波%江北 or 宁波%北仑 or 浙江%北仑 or 宁波%镇海 or 浙江%镇海 or 宁波%鄞州 or 鄞县 or 浙江%慈溪 or 宁波%慈溪 or 慈溪县 or 浙江%余姚 or 宁波%余姚 or 余姚县 or 浙江%奉化 or 宁波%奉化 or 奉化县 or 浙江%宁海 or 宁波%宁海 or 浙江%象山 or 宁波%象山 or 宁波%国家高新区 or 宁波%科技园区 or 宁波%保税区 or 宁波%大榭开发区 or 宁波%东钱湖旅游度假区))))  and 地址=(( (315%浙江省宁波市 or 浙江%宁波 or 宁波%海曙 or 浙江%海曙 or 宁波%江东 or 宁波%江北 or 宁波%北仑 or 浙江%北仑 or 宁波%镇海 or 浙江%镇海 or 宁波%鄞州 or 鄞县 or 浙江%慈溪 or 宁波%慈溪 or 慈溪县 or 浙江%余姚 or 宁波%余姚 or 余姚县 or 浙江%奉化 or 宁波%奉化 or 奉化县 or 浙江%宁海 or 宁波%宁海 or 浙江%象山 or 宁波%象山 or 宁波%国家高新区 or 宁波%科技园区 or 宁波%保税区 or 宁波%大榭开发区 or 宁波%东钱湖旅游度假区)))",
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