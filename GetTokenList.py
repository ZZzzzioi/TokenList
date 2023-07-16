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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from random import randint
import requests
import json


# Open Chrome and Access the Website
def OpenChromeDriver():
    option = webdriver.ChromeOptions()
    option.add_argument('--start-maximized')  # 最大化运行（全屏窗口）设置元素定位比较准确
    option.add_argument(
        '--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    )
    option.add_argument('blink-settings=imagesEnabled=false')

    driver = webdriver.Chrome(options=option)
    return driver


# Get trading pair amount and info
def GetTradingPairs(driver, URL):
    driver.get(URL)
    WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/main/div[2]/div/div[1]/div[2]/div[1]/h1")))
    amount = driver.find_element(By.XPATH, '/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[1]/div[1]/div[3]/div[1]').text
    TradingPairLists = []
    for i in range(1, int(amount)+1):
        try:
            WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/table/tbody/tr[{}]/td[4]'.format(i))))
        except:
            break
        TradingPairName = driver.find_element(By.XPATH, '/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/table/tbody/tr[{}]/td[4]'.format(i)).text
        TradingPairName = TradingPairName.split('/')
        if i % 50 == 0:
            WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/div/a/span')))
            driver.find_element(By.XPATH, '/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/div/a/span').click()
        TradingPairLists.append(TradingPairName[0])
        print(i)
    TradingPairLists = list(set(TradingPairLists))
    return driver, TradingPairLists


# Get Token MC and FDV
def GetTokenInfo(driver, TradingPairLists, state):
    TokenInfoLists = []
    for token in TradingPairLists:
        for token_gecko in state:
            if token.lower() == token_gecko['symbol']:
                token_id = token_gecko['id']
                break
            else:
                continue
        
        driver.get('https://www.coingecko.com/en/coins/{}'.format(token_id))
        time.sleep(randint(5, 8))
        WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/div/a/span')))
        html = driver.page_source
        TokenAddress = driver.current_url

        html_BS4 = BeautifulSoup(html, 'lxml')
        TokenName = html_BS4.find(class_='tw-font-bold tw-text-gray-900 dark:tw-text-white dark:tw-text-opacity-87 md:tw-text-xl tw-text-lg tw-ml-2 tw-mr-1').text.replace('\n', '')
        TokenPrice = html_BS4.find(class_='tw-text-gray-900 dark:tw-text-white tw-text-3xl').find(class_='no-wrap').text.replace('$', '').replace(',', '')

        InfoTable = html_BS4.find(class_='tw-col-span-2 lg:tw-col-span-2')
        InfoTables = InfoTable.find_all(class_='tw-grid tw-grid-cols-2')
        TokenMC = InfoTables[-1].find(string='\nMarket Cap\n').parent.parent.find(class_='no-wrap').text.replace('$', '').replace(',', '')
        TokenFDV = InfoTables[-1].find(string='\nFully Diluted Valuation\n').parent.parent.find(class_='no-wrap').text.replace('$', '').replace(',', '')
        McFdv = float(TokenMC) / float(TokenFDV)

        TokenInfoLists.append([TokenName, token, TokenAddress, TokenPrice, TokenMC, TokenFDV, McFdv])
        print(token)
    return driver, TokenInfoLists


def save_file(Data, col_name, save_address):
    Name = col_name
    TokenData = pd.DataFrame(data=Data, columns=Name)
    TokenData.to_excel(save_address)


def main():
    ExchangeURL = ['https://www.coingecko.com/en/exchanges/coinbase-exchange', 'https://www.coingecko.com/en/exchanges/binance'
                   'https://www.coingecko.com/en/exchanges/okx', 'https://www.coingecko.com/en/exchanges/upbit']
    driver = OpenChromeDriver()

    # Get exchange trading pairs and save it as xlsx
    TradingPairs_all = []
    for exchange in ExchangeURL:
        driver, TradingPairLists = GetTradingPairs(driver, exchange)
        exchangeName = exchange.replace('https://www.coingecko.com/en/exchanges/', '')
        col_name = ['token']
        save_address = '{}_OnlyPairs.xlsx'.format(exchangeName)
        save_file(TradingPairLists, col_name, save_address)
        TradingPairs_all = list(set(TradingPairs_all).union(set(TradingPairLists)))
        time.sleep(5)
    
    # Get token info from coingecko API
    TokenList_Coingecko = requests.get('https://api.coingecko.com/api/v3/coins/list')
    state = json.loads(TokenList_Coingecko.text)

    driver, TokenInfoLists = GetTokenInfo(driver, TradingPairs_all, state)
    TokenInfo_colname = ['TokenName', 'token', 'TokenAddress', 'TokenPrice', 'TokenMC', 'TokenFDV', 'McFdv']
    TokenInfo_data = TokenInfoLists
    Tokeninfo_save_address = 'TokenInfo.xlsx'
    save_file(TokenInfo_data, TokenInfo_colname, Tokeninfo_save_address)


if __name__ == 'main':
    main()
