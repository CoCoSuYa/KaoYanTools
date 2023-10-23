import os
import subprocess
import time
from appium.webdriver.common.appiumby import AppiumBy
from selenium import webdriver as selenium_webdriver
from appium import webdriver as appium_webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.options import Options

local_url = "screenshot.png"
device_url = "mnt/shared/Pictures/screenshot.png"
# 启动 Chrome 并设置端口号为9222
subprocess.Popen(['C:/Program Files/Google/Chrome/Application/chrome.exe', '--remote-debugging-port=9222'])
print("Chrome启动成功")

# 连接到端口号为9222的 Chrome
web_options = Options()
web_options.add_experimental_option("debuggerAddress", "localhost:9222")
web_driver = selenium_webdriver.Chrome(options=web_options)
print("连接Chrome浏览器成功")

# 控制浏览器跳转小红书登录页面并在三秒后截图保存
web_driver.get('https://www.xiaohongshu.com/explore')
time.sleep(5)
web_driver.save_screenshot(local_url)

# push截图到设备上并删除本地截图
adb_command = ['adb', 'push', local_url, device_url]
subprocess.run(adb_command, check=True)
# 用 adb shell 命令通知媒体扫描器扫描新文件,启动系统图库应用
subprocess.run(['adb', 'shell', 'am', 'start', '-n',
                'com.android.gallery3d/.app.Gallery'], check=True)
# 检查本地截图是否存在
if os.path.exists(local_url):
    # 删除截图
    os.remove(local_url)
    print(f"{local_url} 本地已删除")
else:
    print(f"{local_url} 本地找不到")

# 定义Desired Capabilities
desired_caps = {
    "appium:platformName": "Android",
    "appium:platformVersion": "7.1.2",
    "appium:deviceName": "emulator-5554",
    "appium:automationName": "UiAutomator2",
    "appium:appPackage": "com.xingin.xhs",
    "appium:appActivity": "com.xingin.xhs.index.v2.IndexActivityV2"
}
# 连接到Appium服务器
app_driver = appium_webdriver.Remote("http://localhost:4723/wd/hub", desired_caps)
app_driver.implicitly_wait(10)

# 同意弹窗隐私协议
protocol_accept_pop = app_driver.find_element(by=AppiumBy.ID, value="com.xingin.xhs:id/d_e")
protocol_accept_pop.click()
print("同意弹窗隐私协议")
# 同意登录协议
protocol_accept_login = app_driver.find_element(by=AppiumBy.ID, value="com.xingin.xhs:id/en8")
protocol_accept_login.click()
print("同意登录协议")
# 点击登录按钮
login = app_driver.find_element(by=AppiumBy.ID, value="com.xingin.xhs:id/dg4")
login.click()
print("点击登录按钮")
# 检查微博是否默认授权，未默认授权则点击，默认授权则等待2s页面刷新
try:
    empower_accept = app_driver.find_element(by=AppiumBy.ID, value="com.sina.weibo:id/new_bnLogin")
    print("微博未默认授权")
    time.sleep(1)
    print("点击授权按钮")
    empower_accept.click()
except NoSuchElementException:
    print("微博已默认授权")
    time.sleep(1)
# 等待新手引导结束
time.sleep(10)
# 跳转"我的"页面
my_btn = app_driver.find_element(by=AppiumBy.ID, value="com.xingin.xhs:id/cco")
print("跳转我的页面")
my_btn.click()
# 拉起列表页
list_btn = app_driver.find_element(by=AppiumBy.ID, value="com.xingin.xhs:id/eo5")
print("拉起侧边列表")
list_btn.click()
# 打开扫一扫
Code_Scan = app_driver.find_element(by=AppiumBy.ID, value="com.xingin.xhs:id/b0t")
print("打开扫一扫功能")
Code_Scan.click()
# 授权使用相机
camera_empower = app_driver.find_element(by=AppiumBy.ID, value="com.android.packageinstaller:id/permission_allow_button")
print("授权使用相机")
camera_empower.click()
# 打开相册
photo_open = app_driver.find_element(by=AppiumBy.ID, value="com.xingin.xhs:id/d2z")
print("打开相册")
photo_open.click()
# 授权使用相册
photo_empower = app_driver.find_element(by=AppiumBy.ID, value="com.android.packageinstaller:id/permission_allow_button")
print("授权使用相册")
photo_empower.click()
# 选择截图
photo_select = app_driver.find_element(by=AppiumBy.ID, value="com.xingin.xhs:id/c92")
print("选择截图开始扫码")
photo_select.click()
# 等待跳转授权
time.sleep(3)
# 授权web端登录
protocol_accept_login = app_driver.find_element(by=AppiumBy.XPATH, value="/hierarchy/android.widget.FrameLayout"
                                                                         "/android.widget.FrameLayout/android.widget"
                                                                         ".LinearLayout/android.widget.FrameLayout"
                                                                         "/android.widget.LinearLayout/android.widget"
                                                                         ".FrameLayout/android.widget.FrameLayout"
                                                                         "/android.widget.FrameLayout/android.widget"
                                                                         ".FrameLayout/android.widget.FrameLayout"
                                                                         "/android.view.ViewGroup/android.view"
                                                                         ".ViewGroup/android.view.ViewGroup/android"
                                                                         ".view.ViewGroup/android.view.ViewGroup"
                                                                         "/android.view.ViewGroup/android.view"
                                                                         ".ViewGroup/android.view.ViewGroup[4]")
protocol_accept_login.click()
print("授权web登录协议")
# 点击登录按钮
login = app_driver.find_element(by=AppiumBy.XPATH, value="/hierarchy/android.widget.FrameLayout/android.widget"
                                                         ".FrameLayout/android.widget.LinearLayout/android.widget"
                                                         ".FrameLayout/android.widget.LinearLayout/android.widget"
                                                         ".FrameLayout/android.widget.FrameLayout/android.widget"
                                                         ".FrameLayout/android.widget.FrameLayout/android.widget"
                                                         ".FrameLayout/android.view.ViewGroup/android.view.ViewGroup"
                                                         "/android.view.ViewGroup/android.view.ViewGroup/android.view"
                                                         ".ViewGroup/android.view.ViewGroup/android.view.ViewGroup"
                                                         "/android.view.ViewGroup[2]")
login.click()
print("点击登录按钮")
# 结束测试后，关闭driver
app_driver.quit()
time.sleep(5)
print("cookie_list:", web_driver.get_cookies())
cookie_list = web_driver.get_cookies()
cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookie_list}
print("cookie_dict:", cookie_dict)
web_driver.quit()
# 保存cookie
