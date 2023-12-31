# -*- coding: utf-8 -*-
"""
Created on 2023.06.12
@author: Zisheng Ji
"""

from selenium import webdriver
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
from selenium.common.exceptions import TimeoutException


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
        except (TimeoutError, TimeoutException):
            break

        TradingPairName_row = driver.find_element(By.XPATH, '/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/table/tbody/tr[{}]/td[2]'.format(i)).text
        if '/' in TradingPairName_row:
            TradingPairName_all = TradingPairName_row.split('/')[0]
        else:
            TradingPairName_all = TradingPairName_row
        TradingPairName_all = TradingPairName_all.rstrip(' ')
        
        TradingPairName = driver.find_element(By.XPATH, '/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/table/tbody/tr[{}]/td[4]'.format(i)).text
        TradingPairName = TradingPairName.split('/')
        if i % 50 == 0:
            WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/div/a/span')))
            driver.find_element(By.XPATH, '/html/body/div[2]/main/div[3]/div[1]/div[3]/div/div[1]/div/div[2]/div/a/span').click()
        TradingPairLists.append([TradingPairName[0], TradingPairName_all])
        print(i, amount)
    TradingPairLists = [list(t) for t in set(tuple(_) for _ in TradingPairLists)]
    return driver, TradingPairLists


# Get Token MC and FDV
def GetTokenInfo(TradingPairLists, state):
    TokenWebsite = []
    NotFoundToken = []
    for token in TradingPairLists:
        for token_gecko in state:
            if token[1].count('.') >= 3:
                if token[0].lower() == token_gecko['symbol'] and token[1].replace('.', '') in token_gecko['name'].replace('.', ''):
                    token_id = token_gecko['id']
                    TokenWebsite.append(token_id)
                    break
                elif token_gecko == state[-1]:
                    NotFoundToken.append(token)
                else:
                    continue
            else:
                if token[0].lower() == token_gecko['symbol'] and token[1] == token_gecko['name']:
                    token_id = token_gecko['id']
                    TokenWebsite.append(token_id)
                    break
                elif token_gecko == state[-1]:
                    NotFoundToken.append(token)
                else:
                    continue
    TokenWebsite = list(set(TokenWebsite))

    i = 0
    TokenWebsite_list = []
    while (i < len(TokenWebsite)):
        TokenWebsite_list.append(TokenWebsite[i: i+100])
        i += 100
    TokenWebsite_split = ['%2C'.join(i) for i in TokenWebsite_list]

    TokenInfoLists = []
    for TokenList in TokenWebsite_split:
        RequestURL = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={}&order=market_cap_desc&per_page=250&page=1&sparkline=false&locale=en'.format(TokenList)
        TokenRequest = requests.get(RequestURL)
        TokenInfoGeckoAPI = json.loads(TokenRequest.text)

        for Token in TokenInfoGeckoAPI:
            TokenSymbol = Token['symbol']
            TokenName = Token['name']
            TokenAddress = 'https://www.coingecko.com/en/coins/{}'.format(Token['id'])
            TokenPrice = Token['current_price']
            TokenMC = Token['market_cap']
            TokenMCRank = Token['market_cap_rank']
            TokenFDV = Token['fully_diluted_valuation']
            try:
                McFdv = float(TokenMC) / float(TokenFDV)
            except TypeError:
                McFdv = '/'
            except ZeroDivisionError:
                McFdv = '/'
            TokenInfoLists.append([TokenMCRank, TokenName, TokenSymbol, TokenAddress, TokenPrice, TokenMC, TokenFDV, McFdv])
            print(TokenName)
        time.sleep(60)
    return TokenInfoLists


def ExchangeTokenList(save_address):
    ExchangeTradingPair = pd.read_excel(save_address)
    ExchangeListPair = [(ExchangeTradingPair.iloc[i,0], ExchangeTradingPair.iloc[i,1]) for i in range(len(ExchangeTradingPair))]
    return ExchangeListPair


def InquireTokenInfo(TokenList):
    TokenData = pd.read_excel('TokenInfo.xlsx')
    TokenFilter_df = pd.DataFrame()
    NotFoundToken = pd.DataFrame()
    for token in TokenList:
        for i in range(len(TokenData)):
            if token[1].count('.') >= 3:
                if token[0].lower() == TokenData['TokenSymbol'][i] and token[1].replace('.', '') in TokenData['TokenName'][i].replace('.', ''):
                    TokenFilter_df = pd.concat([TokenFilter_df, TokenData.iloc[[i]]])
                    break
                elif i == len(TokenData):
                    NotFoundToken.append(token)
                else:
                    continue
            else:
                if token[0].lower() == TokenData['TokenSymbol'][i] and token[1] == TokenData['TokenName'][i]:
                    TokenFilter_df = pd.concat([TokenFilter_df, TokenData.iloc[[i]]])
                    break
                elif i == len(TokenData):
                    NotFoundToken.append(token)
                else:
                    continue

    TokenFilter_df = TokenFilter_df.drop_duplicates()
    return TokenFilter_df


def save_file(Data, col_name, save_address):
    Name = col_name
    TokenData = pd.DataFrame(data=Data, columns=Name)
    TokenData.to_excel(save_address, index=False)


def main():
    ExchangeURL = ['https://www.coingecko.com/en/exchanges/coinbase-exchange', 
                   'https://www.coingecko.com/en/exchanges/binance',
                   'https://www.coingecko.com/en/exchanges/okx', 'https://www.coingecko.com/en/exchanges/upbit']
    driver = OpenChromeDriver()

    # Get exchange trading pairs and save it as xlsx
    # 在抓取的时候可能会出现点击下一页点不到的问题，需要手动点一下
    TradingPairs_all = []
    for exchange in ExchangeURL:
        driver, TradingPairLists = GetTradingPairs(driver, exchange)
        exchangeName = exchange.replace('https://www.coingecko.com/en/exchanges/', '')
        col_name = ['symbol', 'name']
        save_address = '{}_OnlyPairs.xlsx'.format(exchangeName)
        save_file(TradingPairLists, col_name, save_address)
        TradingPairs_all = list(set(tuple(_) for _ in TradingPairs_all).union(set(tuple(_) for _ in TradingPairLists)))
        time.sleep(5)
    driver.quit()
    save_file(TradingPairs_all, ['symbol', 'name'], 'TradingPairs_all.xlsx')

    '''
    binance = pd.read_excel('binance_OnlyPairs.xlsx')
    coinbase = pd.read_excel('coinbase-exchange_OnlyPairs.xlsx')
    okx = pd.read_excel('okx_OnlyPairs.xlsx')
    upbit = pd.read_excel('upbit_OnlyPairs.xlsx')

    blist = [(binance.iloc[i,0], binance.iloc[i,1]) for i in range(len(binance))]
    clist = [(coinbase.iloc[i,0], coinbase.iloc[i,1]) for i in range(len(coinbase))]
    olist = [(okx.iloc[i,0], okx.iloc[i,1]) for i in range(len(okx))]
    ulist = [(upbit.iloc[i,0], upbit.iloc[i,1]) for i in range(len(upbit))]
    TradingPairs_all = list(set(blist).union(set(clist)).union(set(olist)).union(set(ulist)))
    '''

    # Get token info from coingecko API
    TokenList_Coingecko = requests.get('https://api.coingecko.com/api/v3/coins/list')
    state = json.loads(TokenList_Coingecko.text)

    TokenInfo_colname = ['TokenMCRank', 'TokenName', 'TokenSymbol', 'TokenAddress', 'TokenPrice', 'TokenMC', 'TokenFDV', 'McFdv']
    Tokeninfo_save_address = 'TokenInfo.xlsx'
    TokenInfoData = GetTokenInfo(TradingPairs_all, state)
    save_file(TokenInfoData, TokenInfo_colname, Tokeninfo_save_address)

    # Get the intersection of the exchange
    binance = ExchangeTokenList('binance_OnlyPairs.xlsx')
    coinbase = ExchangeTokenList('coinbase-exchange_OnlyPairs.xlsx')
    okx = ExchangeTokenList('okx_OnlyPairs.xlsx')
    upbit = ExchangeTokenList('upbit_OnlyPairs.xlsx')

    coinbase_upbit = list(set(coinbase).intersection(set(upbit)))
    bn_cb_okx = list(set(coinbase).intersection(set(okx)).intersection(set(binance)))

    coinbase_upbit_info = InquireTokenInfo(coinbase_upbit)
    bn_cb_okx_info = InquireTokenInfo(bn_cb_okx)

    save_file(coinbase_upbit_info, TokenInfo_colname, 'coinbase_upbit_info.xlsx')
    save_file(bn_cb_okx_info, TokenInfo_colname, 'bn_cb_okx_info.xlsx')


if __name__ == 'main':
    main()
