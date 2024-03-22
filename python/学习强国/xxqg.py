import random
import time
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 记录跳转的URL列表
visited_urls = set()


def last_page_size(driver, size):
    """
    滚动到页面底部
    :param driver: WebDriver对象
    :param size: 滚动次数
    :return: 滚动后的WebDriver对象
    """
    # 获取当前页面的高度
    page_height = driver.execute_script("return document.documentElement.scrollHeight")
    random_number = random.random() * 0.1
    # 计算要滚动的距离
    scroll_distance = int(page_height * random_number)  # 滚动到页面高度的 0-10% 处
    # 页面向下滚动一段距离
    for _ in range(size):
        driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
    return driver


def last_page(driver):
    """
    滚动到页面底部
    :param driver: WebDriver对象
    :return: 滚动后的WebDriver对象
    """
    # 获取当前页面的高度
    page_height = driver.execute_script("return document.documentElement.scrollHeight")
    random_number = random.random() * 0.1
    # 计算要滚动的距离
    scroll_distance = int(page_height * random_number)  # 滚动到页面高度的 0-10% 处
    # 页面向下滚动一段距离
    driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
    return driver


def click(driver):
    """
    在页面上随机点击
    :param driver: WebDriver对象
    :return: 点击后的WebDriver对象
    """
    # 获取页面宽度和高度
    window_width = driver.execute_script(
        "return window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;")
    window_height = driver.execute_script(
        "return window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;")
    # 计算中间范围的宽度和高度
    middle_width = int(window_width * 0.7)
    middle_height = int(window_height * 0.7)
    middle_x = int((window_width - middle_width) / 2)
    middle_y = int((window_height - middle_height) / 2)
    # 随机生成点击位置
    click_x = random.randint(middle_x, middle_x + middle_width)
    click_y = random.randint(middle_y, middle_y + middle_height)
    # 执行点击操作
    click_script = f"document.elementFromPoint({click_x}, {click_y}).click();"
    driver.execute_script(click_script)
    # 切换到新页面
    new_window = driver.window_handles[-1]
    driver.switch_to.window(new_window)
    return driver


def scroll_to_section(driver):
    """
    滚动到指定的section元素并点击
    :param driver: WebDriver对象
    :return: 点击后的WebDriver对象
    """
    # 找到指定 section 元素
    section = driver.find_element(By.ID, "f813")
    # 获取 section 元素相对于当前窗口的位置
    section_position = section.location_once_scrolled_into_view
    # 将页面向下滚动 50 像素
    scroll_distance = 50
    target_position = section_position["y"] + scroll_distance
    driver.execute_script(f"window.scroll(0, {target_position});")
    # 在 section 元素上点击
    section.click()
    return driver


def click_on_div(driver):
    """
    点击指定的div元素
    :param driver: WebDriver对象
    :return: 点击后的WebDriver对象
    """
    # 找到指定的 div 元素
    div = driver.find_element(By.CSS_SELECTOR, "div.next.handle")
    # 创建 ActionChains 对象
    actions = ActionChains(driver)
    # 将鼠标移动到 div 元素的左边 200 像素的位置
    actions.move_to_element(div).move_by_offset(-200, 0).click().perform()
    return driver


def click_on_span(driver):
    """
    点击指定的span元素
    :param driver: WebDriver对象
    :return: 点击后的WebDriver对象
    """
    # 找到指定的 span 元素
    span = driver.find_element(By.CSS_SELECTOR, "span.linkSpan")
    # 点击 span 元素
    span.click()
    return driver


def click_on_random_span(driver):
    """
    随机点击符合条件的span元素
    :param driver: WebDriver对象
    :return: 点击后的WebDriver对象
    """
    # 找到所有的 span 元素
    spans = driver.find_elements(By.CSS_SELECTOR, "span[style='cursor: initial;']")
    # 如果 span 元素存在
    if spans:
        # 遍历所有 span 元素
        for span in spans:
            # 检查 span 元素的文本内容是否为 "重要新闻"
            if span.text == "重要新闻":
                driver = click(driver)
                driver = look_or_watch(driver)
    else:
        print("没有找到符合条件的 span 元素,正在重新打开重要新闻")
        driver = back_windows(driver, 0)
        driver.execute_script(f"window.scrollBy(0, {200});")
        time.sleep(5)
        driver = click_on_span(driver)
    return driver


def back_windows(driver, index):
    """
    切换窗口到指定的索引，并关闭其他窗口
    :param driver: WebDriver对象
    :param index: 窗口索引
    :return: 切换后的WebDriver对象
    """
    # 获取所有窗口的句柄
    window_handles = driver.window_handles
    # 切换到第一个窗口
    driver.switch_to.window(window_handles[index])
    # 关闭其他窗口
    for handle in window_handles[index + 1:]:
        driver.switch_to.window(handle)
        driver.close()
    # 切换回第一个窗口
    driver.switch_to.window(window_handles[index])
    return driver


def look_or_watch(driver):
    """
    查看文章或观看视频
    :param driver: WebDriver对象
    :return: 处理后的WebDriver对象
    """
    global yd_count
    global sp_count
    # 判断元素是否存在
    try:
        element = driver.find_element('css selector', '[class*="prism-big-play-btn"]')
        # element = driver.find_element('css selector', 'div.outter')
        if element is not None:
            if sp_count < 12:
                element.click()
                print('点击了视频,观看63S')
                time.sleep(63)
                sp_count += 1
            else:
                print('观看视频次数达到')
        else:
            if yd_count < 12:
                print('识别阅读-----阅读75秒')
                page_height = driver.execute_script("return document.documentElement.scrollHeight")
                scroll_distance = int(page_height / 5)
                # 下拉5次
                for _ in range(15):
                    driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                    time.sleep(5)
                yd_count += 1
            else:
                print('阅读次数达到')
    except:
        if yd_count < 12:
            print('识别阅读-----阅读75秒')
            page_height = driver.execute_script("return document.documentElement.scrollHeight")
            scroll_distance = int(page_height / 5)
            # 下拉5次
            for _ in range(15):
                driver.execute_script(f"window.scrollBy(0, {scroll_distance});")
                time.sleep(5)
            yd_count += 1
        else:
            print('阅读次数达到')
    return driver


import re


def check_score(driver):
    """
    检查分数
    :param driver: WebDriver对象
    :return: 处理后的WebDriver对象
    """
    global yd_count, sp_count
    driver.get('https://pc.xuexi.cn/points/my-points.html')
    wait = WebDriverWait(driver, 10)
    try:
        wz = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'my-points-card-text')))
    except TimeoutException:
        print("页面加载超时")
    current_url = driver.current_url
    print("当前URL:", current_url)
    wenzhang = driver.find_elements(By.CLASS_NAME, 'my-points-card-text')
    wenzhang_count = 1
    for i in wenzhang:
        print(i.text)
        if '/' in i.text:
            scores = re.findall(r'\d+', i.text)
            if len(scores) == 2:
                if wenzhang_count == 2:
                    yd_count = int(scores[0])
                if wenzhang_count == 3:
                    sp_count = int(scores[0])
        wenzhang_count = wenzhang_count + 1
    print("阅读分数:", yd_count)
    print("视频分数:", sp_count)
    while True:
        new_url = driver.current_url
        if 'login.html' in new_url:
            print('请扫码')
            time.sleep(10)
        else:
            write_cookie(driver)
            driver.get('https://www.xuexi.cn/')
            break
    return driver


def sbxh(driver):
    global yd_count
    global sp_count
    count_size = 0
    while True:
        driver = last_page(driver)
        time.sleep(2)
        driver = click(driver)
        time.sleep(5)
        count = 1
        while yd_count < 12 or sp_count < 12:
            print('阅读次数{}'.format(yd_count))
            print('视频次数{}'.format(sp_count))
            # if (yd_count >= 12 and sp_count > 10) or (sp_count >= 12 and yd_count > 10):
            #     check_score(driver)
            #     if yd_count == 12 and sp_count == 12:
            #         print('-----finish-------')
            #         break
            new_url = driver.current_url
            print("跳转后的页面 URL：", new_url)
            if str(new_url).__eq__('https://www.xuexi.cn/'):
                okBtn = driver.find_elements(By.CSS_SELECTOR, "dev[class='okBtn']")
                if okBtn:
                    driver.refresh()
                    # okBtn.click()
                    # try:
                    #     driver = back_windows(driver, 0)
                    #     print('点击确认--------------')
                    # except:
                    #     pass
                count = count + 1
                time.sleep(2)
                driver = click(driver)
                print('重新点击')
                if count > 3:
                    print('重新跳转')
                    driver.get('https://www.xuexi.cn/')
                    driver.refresh()
                    driver = last_page_size(driver, count_size % 20)
                    count = 1
                    break
            elif str(new_url).__contains__('edge'):
                driver.get('https://www.xuexi.cn/')
                driver.refresh()
                driver = last_page_size(driver, count_size % 20)
                count = 1
                break
            else:
                # 判断driver.current_url是否在visited_urls中不存在
                if driver.current_url not in visited_urls:
                    visited_urls.add(driver.current_url)
                    driver = last_page(driver)
                    time.sleep(5)
                    driver = look_or_watch(driver)
                try:
                    driver = back_windows(driver, 0)
                except:
                    pass
                time.sleep(1)
                break
        if count_size % 20 == 0:
            scroll_script = f"window.scrollBy(0, -1000);"
            print('重新拉取')
            # 获取分数
            check_score(driver)
        count_size += 1
        if yd_count == 12 and sp_count == 12:
            print('-----finish-------')
            break
        # if yd_count >= 12 or sp_count >= 12:
    #     check_score(driver)
    #   if yd_count == 12 and sp_count == 12:
    #        print('-----finish-------')
    #       break
    # if count_size > 200:
    #     count_size = 0
    #     sleep(4 * 60 * 60)
    return driver


def write_cookie(driver):
    cookies = driver.get_cookies()
    print(cookies)
    filtered_cookies = [cookie for cookie in cookies if cookie['domain'] != 'pc.xuexi.cn']
    with open('cookies.txt', 'w') as file:
        for cookie in filtered_cookies:
            file.write(f"{cookie}\n")


def run():
    global yd_count
    global sp_count
    yd_count = 0
    sp_count = 0
    webdriver_path = "chromedriver.exe"
    driver = webdriver.Chrome(executable_path=webdriver_path)
    driver.get('https://www.xuexi.cn/')
    driver.maximize_window()
    time.sleep(2)
    with open('cookies.txt', 'r') as file:
        cookies = file.readlines()
    # 去除每行末尾的换行符
    cookies = [cookie.strip() for cookie in cookies]
    # 将 cookie 加载到浏览器中
    for cookie in cookies:
        cookie_dict = eval(cookie)
        driver.add_cookie(cookie_dict)

    driver.get('https://www.xuexi.cn/')
    driver.refresh()
    time.sleep(3)
    check_score(driver)
    driver = last_page_size(driver, 5)
    while yd_count <= 12 and sp_count <= 12:
        driver = sbxh(driver)
        if (yd_count >= 12 and sp_count > 10) or (sp_count >= 12 and yd_count > 10):
            check_score(driver)
            if yd_count >= 12 and sp_count >= 12:
                print('分数达到，休眠3小时')
                time.sleep(3 * 60 * 60)
    driver.quit()


run()
