import argparse
import re

import time

import requests

from boj import BOJ



parser =  argparse.ArgumentParser()
parser.add_argument("--id", type = str, required = True, help = "BOJ ID")
parser.add_argument("--pwd", type = str, required = True, help = "BOJ Password")
args = parser.parse_args()

BOJ_URL = "https://www.acmicpc.net/"



def login_boj(info):
    url = BOJ_URL+'/'+'signin'
    data = {'login_user_id': info.user_id,'login_password': info.user_pwd}
    res = requests.post(url = url, data = data, allow_redirects = False)



    

if __name__ == "__main__":
    boj = BOJ(args.id, args.pwd)
    boj.crawling()
