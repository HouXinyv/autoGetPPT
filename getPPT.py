"""
实现b站网课截ppt

Author: 侯小喵
Version: 1.0

首先要保证有chrome浏览器。安装对应库。运行后需要在opening_song时间内完成登录，关闭弹幕。之后可以移动打开的浏览器到旮旯里。目前不支持小化
参数设定部分用于设定各个参数，以及网课链接url。
debug模式下会保存每个截图，截图文件名最后一个数为和上一截屏的相似度，据此修改各个阈值。
最终经过筛选的截图会被放入save_path文件夹下
每次运行注意清空一下save_path或debug_path文件夹，避免出现错误
暂时没加隐藏
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
import cv2
import time
import numpy as np
from selenium.webdriver.support.wait import WebDriverWait
import os
import shutil
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchWindowException


# 函数功能：截去字幕部分
# 输入参数：图像的数组，字幕高度占屏幕高度百分比
# 输出参数：去除字幕部分后的灰度图像
def remove_subtitle(img1_path, subtitle_h):
    img1 = cv2.imread(img1_path)
    gray_img_array = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    height, width = gray_img_array.shape[:2]
    new_height = int(height * (1-subtitle_h))
    cropped_img = gray_img_array[0:new_height, 0:width]
    return cropped_img


# 函数功能：比较两张ppt的相似度
# 输入参数：两张图片
# 输出参数：相似度
def calc_image_similarity(img1_path, img2_path, subtitle_h):
    # 读取图片，去除字幕，灰度处理
    img1 = remove_subtitle(img1_path, subtitle_h)
    img2 = remove_subtitle(img2_path, subtitle_h)
    # cv2.imshow('img1',img1)
    # cv2.waitKey(0)
    # 计算MSE和函数所用时间
    start_time = time.time()
    dif = np.count_nonzero(img1 - img2)/img1.size
    end_time = time.time()
    similarity = (1-dif)
    # return {"similarity": similarity, "time": end_time - start_time}
    return similarity


def share_browser():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

    # path是你自己的chrome浏览器的文件路径
    # path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    # chrome_options.binary_location = path

    browser = webdriver.Chrome()  # options=chrome_options, 将这个参数放入，实现隐藏浏览器
    return browser


if __name__ == "__main__":
    # 参数设定
    debug = True  # 可以通过debug来观察 调各个参数
    t_delay = 3  # 截屏间隔，间隔越小，越占cpu，漏截可能越小,单位ms
    new_threshold = 0.9  # 相似度<new_threshold : 出现一页新的ppt
    change_threshold = 0.95  # new_threshold<相似度<change_threshold : ppt发生了变化，重新截屏替换
    subtitle_h = 0.08  # 字幕高度占屏幕高度百分比
    opening_song = 3  # 片头曲部分时长，单位s，留一定时间登录
    save_path = ".\\first_chapter\\"
    debug_path = '.\\debug\\'
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    if not os.path.exists(debug_path):
        os.makedirs(debug_path)

    # 打开网页，定位元素
    # path = 'chromedriver.exe'
    url = 'https://www.bilibili.com/video/BV1c4411d7jb?p=3&vd_source=3cfe9e494bdb757a3e39c25fbf6b783c'  # 视频链接
    # if debug is True:
    #     browser = webdriver.Chrome(path)
    # else:
    browser = share_browser()
    wait = WebDriverWait(browser, 10, 0.5)
    browser.get(url)
    wait.until(lambda divers: browser.find_element(By.XPATH, '//video'))
    video = browser.find_element(By.XPATH, '//video')

    # 截屏比较，正确保存
    time.sleep(opening_song)  # 跳过片头曲
    filename = 1
    debug_num = 1
    video.screenshot(save_path+str(filename)+".png")
    while 1:  # 等关闭浏览器后，退出循环
        try:
            time.sleep(t_delay)
            video.screenshot(save_path + "temp.png")
            similarity = calc_image_similarity(save_path+"temp.png", save_path+str(filename)+".png", subtitle_h)
            if debug is True:
                debug_final_path = debug_path + str(debug_num) + " " + str(filename) + ' ' + str(similarity) + ".png"
                shutil.copyfile(save_path + "temp.png", debug_final_path)
            print(debug_num)
            print(similarity)
            debug_num += 1
            if similarity <= new_threshold:  # 新的一页ppt  起新名字保存
                filename += 1
                os.rename(save_path + "temp.png", save_path + str(filename) + ".png")
            elif new_threshold < similarity <= change_threshold:  # 原来ppt发生了更新 旧名字替换
                os.replace(save_path + "temp.png", save_path + str(filename) + ".png")
        except NoSuchWindowException:
            print("------------------------------你已关闭浏览器-----------------------------")
            break
        except FileExistsError:
            print("你目前的保存路径或debug路径中已经有文件，请检查后重试！！")
            break




