import os
import requests
import time
import threading
from urllib.parse import urlencode
import extensions

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pyperclip

from Exceptions import *
from FileElements import SubmitRecord

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

    def make_code_file(problem_num, language, dir_):
        extension = extensions.extension_name[language]

        file_name = problem_num + '.' + extension

        return open(os.path.join(dir_, file_name), 'w+', encoding='utf-8')

    def get_problem_list(self, driver):
        if '@' in self.user_id:
            self.id = self.user_id.split('@')[0]
        problem_list_url = PROBLEM_URL + self.id
        driver.get(problem_list_url)
        print(problem_list_url)
        driver.implicitly_wait(10)
        time.sleep(4)
        #u-solved
        problem_list = []
        correct_count = int(driver.find_element_by_css_selector("#u-solved").text)
        for i in range(1,correct_count+1):
            problem_list.append(driver.find_element_by_css_selector(f'div.panel-body > a:nth-child({i})').get_attribute('href'))

        return problem_list

    def parsing_problems(self, problem_list):
        self.problems = []
        for p_l in problem_list:
            problem = p_l.split('/')[-1]
            self.problems.append(problem)

    def analyze_problem(self, problem_num, driver):
        url = 'https://www.acmicpc.net/status?'
        query = {'problem_id': problem_num, 'user_id': self.id, 'result_id': '4', 'language_id': '-1', 'from_mine': '1'}

        for k, v in query.items():
            url += k + '=' + v + '&'

        table = dict()
        driver.get(url)
        driver.implicitly_wait(2)
        
        screenLock = threading.Lock()
        
        rows = driver.find_elements_by_xpath('/html/body/div[2]/div[2]/div[3]/div[6]/div/table/tbody/tr')
        if len(rows) is 0:
            return table
        for row in rows:
            html = row.get_attribute('outerHTML')
            content = BeautifulSoup(html,'html.parser')
            columns = content.findAll('td')
            language = columns[6].text
            length_text = columns[7].text.strip()
            if len(length_text) != 0:
                length = length_text.split()[0]
            judge_id = columns[0].text
            element = SubmitRecord(judge_id=judge_id,
            mem=columns[4].contents[0],
            time=columns[5].contents[0],
            code_len=length)

            if table.get(language) is None:
                table[language] = element
            else:
                table[language] = min(table[language], element)
        problem_name = columns[2].a['data-original-title']
        screenLock.acquire()
        print('{:5s} {}'.format(problem_num, problem_name))
        for l, e in table.items():
            print('\t{:10s} {}'.format(l, e))
        screenLock.release()

        return table

    def down_file(self, driver, judge_id):
        url = 'https://www.acmicpc.net/source/'+str(judge_id)
        driver.get(url)
        time.sleep(0.5)

        elem = driver.find_element_by_css_selector("> div.CodeMirror-code").text
        return elem
        
    def get_and_make(self, problem_num, driver, dir_):
        submitted_codes = self.analyze_problem(problem_num, driver)

        for language, source_code in submitted_codes.items():
            with self.make_code_file(problem_num, language, dir_) as files:
                download = self.down_file(driver, source_code.judge_id)


    def get_submitted_files(self, problems, driver):
        for problem_num in problems:
            dir_ = problem_num[:len(problem_num)-3]
            if not os.path.exists(dir_):
                os.makedirs(dir_)
            thread_file_maker = threading.Thread(target=self.get_and_make, args=(problem_num, driver, dir_), daemon=False)
            thread_file_maker.start()
            assert False
            
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
        driver.get(LOGIN_URL)
        driver.implicitly_wait(2)
        self.login_boj(driver)
        time.sleep(2)
        driver.implicitly_wait(2)
        problem_list = self.get_problem_list(driver)
        self.parsing_problems(problem_list)

        self.get_submitted_files(self.problems, driver)



        #


        