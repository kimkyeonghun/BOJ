import requests
import time
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pyperclip

from Exceptions import *

LOGIN_URL = 'https://www.acmicpc.net/signin'
PROBLEM_URL = 'http://www.acmicpc.net/user/'
DRIVER_PATH = './webdriver/chrome/chromedriver.exe'

class Infos:
    def __init__(self, user_id, user_pwd):
        self.user_id = user_id
        self.user_pwd = user_pwd

    def _reset(self):
        self.user_id = None
        self.user_pwd = None
    
    def set_id(self, user_id):
        self.user_id = user_id

    def set_pwd(self, user_pwd):
        self.user_pwd = user_pwd


class BOJ(Infos):
    def __init__(self, user_id, user_pwd):
        super().__init__(user_id, user_pwd)

    def set_selenium_options(self):
        options =webdriver.ChromeOptions()
        #options.add_argument('headless')
        #options.add_argument('disable-gpu')
        options.add_experimental_option('excludeSwitches',['enable-logging'])
        driver = webdriver.Chrome(DRIVER_PATH, chrome_options = options)
        return driver

    def get_response(url, header=None, max_tries=10):
        if header is None:
            header = {'User-Agent': "Mozilla/5.0 (Window NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
        remaining_tries = int(max_tries)
        while remaining_tries > 0:
            # try:
            #     return requests.get(url, headers=header)
            # except:
            #     print("Fail to request")
            #     time.sleep(10)
            return requests.get(url, headers=header)
            remaining_tries -=1
        raise ResponseTimeout

    def get_problem_list(self, driver):
        if '@' in self.user_id:
            id = self.user_id.split('@')[0]
        problem_list_url = PROBLEM_URL + id
        driver.get(problem_list_url)
        datas = driver.find_elements_by_css_selector('body > div.wrapper > div.container.content > div.row > div:nth-child(2) > div > div.col-md-9 > div:nth-child(1) > div.panel-body')
        for data in datas:
            print(data)
        
        
    def clipboard_input(self, driver, user_xpath, user_input):
        temp_user_input = pyperclip.paste()  # 사용자 클립보드를 따로 저장

        pyperclip.copy(user_input)
        driver.find_element_by_xpath(user_xpath).click()
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()

        pyperclip.copy(temp_user_input)  # 사용자 클립보드에 저장 된 내용을 다시 가져 옴
        time.sleep(1)


    def login_boj(self, driver):
        #캡챠 우회 로그인 방법
        self.clipboard_input(driver,'//*[@id="login_form"]/div[2]/input', self.user_id)
        time.sleep(3)
        self.clipboard_input(driver,'//*[@id="login_form"]/div[3]/input', self.user_pwd)
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="submit_button"]').click()
        driver.implicitly_wait(10)
    
    def crawling(self):
        driver = self.set_selenium_options()
        driver.implicitly_wait(2)
        # #driver.get(LOGIN_URL)
        # driver.implicitly_wait(2)
        print(self.get_problem_list(driver))

        #self.login_boj(driver)


        