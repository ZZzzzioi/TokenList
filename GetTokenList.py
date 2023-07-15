# -*- coding: utf-8 -*-
"""
Created on 2023.06.12
@author: Zisheng Ji
"""

from selenium import webdriver
import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


# Open Chrome and Access the Website
def OpenChromeDriver(URL):
    option = webdriver.ChromeOptions()
    option.add_argument('--start-maximized')  # 最大化运行（全屏窗口）设置元素定位比较准确
    option.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    )
    option.add_argument('blink-settings=imagesEnabled=false')

    driver = webdriver.Chrome(options=option)
    driver.get(URL)
    return driver


# Get trading pair amount and info
def GetTradingPairs(driver):
    element = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/main/div[2]/div/div[1]/div[2]/div[1]/h1")))
    amount = driver.find_element(By.XPATH, '/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[1]/div[1]/div[3]/div[1]').text
    TradingPairLists = []
    for i in range(1, int(amount)+1):
        try:
            element = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/table/tbody/tr[{}]/td[4]/a'.format(i))))
        except:
            break
        TradingPairName = driver.find_element(By.XPATH, '/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/table/tbody/tr[{}]/td[4]/a'.format(i)).text
        TradingPairName = TradingPairName.split('/')
        if i % 50 == 0:
            element = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/div/a/span')))
            driver.find_element(By.XPATH, '/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/div/a/span').click()
        print(i)
        TradingPairLists.append(TradingPairName[0])
    return driver, TradingPairLists


# Get Token MC and FDV
def 

/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/table/tbody/tr[2]/td[4]/a
/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/table/tbody/tr[1]/td[4]/a
/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/table/tbody/tr[2]/td[4]/a


    # Binance: https://www.coingecko.com/en/exchanges/binance
    # CoinBase: https://www.coingecko.com/en/exchanges/coinbase-exchange
    # OKX: https://www.coingecko.com/en/exchanges/okx
    # Upbit: https://www.coingecko.com/en/exchanges/upbit