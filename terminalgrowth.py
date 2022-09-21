"""
To estimate Perpetual Growth Rate
first created on 26 May 2022
Latest update - 9 Sep 2022

Updates
For Django App testing

"""

import numpy as np
import pandas as pd
#from pandas_datareader import data as wb
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm
import datetime as dt
from datetime import timedelta
from datetime import date
import xlsxwriter
import requests
from bs4 import BeautifulSoup
import string
import math
import lxml
from lxml import html
import time
import random
import html5lib

pd.options.mode.chained_assignment = None  # default='warn'

import yahoo_fin.stock_info as si

#set the number of columns to display
pd.set_option('display.max_columns', 8)


#if there is a suffix to add for certain stocks
suffixToAdd = ""

#set the number of columns to display
pd.set_option('display.max_columns', 8)

#function to make all values numerical
def convert_to_numeric(column):
    first_col = [i.replace(',','') for i in column]
    #second_col = [i.replace('-','') if i.value =='-' for i in first_col ]
    second_col = []
    for i in first_col:
        if (len(i) > 1):
            second_col.append(i)
        else:
            second_col.append(i.replace('-',''))

    third_col = [i.replace('%','') for i in second_col]
    final_col = pd.to_numeric(third_col)

    return final_col



#function to check if symbol is found
#returns symbol_ok is True if a correct symbol is found
def symbol_found(symbol):

    symbol_ok = False

    try:
        #returns data of dictionary type
        data = si.get_quote_data(symbol)
        symbol_name = data['shortName']
        print(symbol_name)

        #exchange must be NY stock exhcange or Nasdaq
        if (data["exchange"]=="NYQ" or data["exchange"]=="NMS"):
            symbol_ok = True
            print(symbol_ok)
        else:
            #symbol found but not from exchanges covered
            print('Error! ' + symbol +' not covered!')
            symbol_ok = False #set symbol_ok to False

        return symbol_ok

    #if symbol is not found then IndexError is handled
    except(IndexError):
        symbol_ok = False    #set symbol_ok to False
        print('Error! ' + symbol +' not found!') #error message
        return symbol_ok


def get_symbol_name(ticker):
    #Symbol Name - to be store in DB
    symbol_name = ''

    try:
        #returns data of dictionary type
        data = si.get_quote_data(ticker)

        #exchange must be NY stock exhcange or Nasdaq
        if (symbol_found(ticker)):
            symbol_name = data['shortName']
        else:
            #symbol found but not from exchanges covered
            symbol_name = "Error"

        return symbol_name

    #if symbol is not found then IndexError is handled
    except(IndexError):
        symbol_name = "Error!" #set error
        return symbol_name

def get_symbol_currency(ticker):
    symbol_name = ''

    try:
        #returns data of dictionary type
        data = si.get_quote_data(ticker)

        #exchange must be NY stock exhcange or Nasdaq
        if (symbol_found(ticker)):
            symbol_currency = data['currency']
        else:
            #symbol found but not from exchanges covered
            symbol_currency = "Error!"

        return symbol_currency

    #if symbol is not found then IndexError is handled
    except(IndexError):
        symbol_currency = "Error!" #set error
        return symbol_currency


#get Beta
def get_yahoo_beta(ticker):

    print("Getting beta for " + ticker)

    #the page to scrape
    analysis_page = "https://finance.yahoo.com/quote/" + ticker + \
                 "/key-statistics?p=" + ticker

    r = requests.get(analysis_page,headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    #print(r)

    #read the tables in the given page
    try:
        tables = pd.read_html(r.text)
        tables_ok = True
        #print(tables)
    except(ValueError):
        tables_ok = False
        print("No statistics tables found for " + ticker)


    if tables_ok:
        #get the tables that are 5 columns only and get rid of the others
        #tables = [table for table in tables if table.shape[1] == 5]

        #get the second table which is the stock history table
        selected_table = tables[1]

        Beta = float(selected_table.iloc[0,1])

        if (math.isnan(Beta) == False):

            print(Beta)
            return Beta
        else:
            Beta = 1
            print("Error in obtaining Beta. Assume Beta = 1")
            return Beta

    else:

        Beta = 1
        print("Error in obtaining Beta. Assume Beta = 1")
        return Beta


def get_yahoo_marketcap(ticker):

    print("Getting market cap for " + ticker)

    #the page to scrape
    analysis_page = "https://finance.yahoo.com/quote/" + ticker + \
                 "/key-statistics?p=" + ticker

    r = requests.get(analysis_page,headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    #print(r)

    #read the tables in the given page
    try:
        tables = pd.read_html(r.text)
        tables_ok = True
    except(ValueError):
        tables_ok = False
        print("No statistics tables found for " + ticker)

    #print(tables)


    if tables_ok:
        #get the tables that are 5 columns only and get rid of the others
        #tables = [table for table in tables if table.shape[1] == 5]

        #get the second table which is the stock history table
        selected_table = tables[0]

        print(selected_table)

        Market_cap_str = (selected_table.iloc[0,1])

        #convert market cap to millions
        if Market_cap_str[-1] == 'T':
            Market_cap = float(Market_cap_str[:-1])

            Market_cap = Market_cap * 1000000        #convert to millions

            print('Market cap = ', str(Market_cap))

        else:
            if Market_cap_str[-1] == 'B':
                Market_cap = float(Market_cap_str[:-1])

                Market_cap = Market_cap * 1000        #convert to millions

                print('Market cap = ', str(Market_cap))
            else:
                if Market_cap_str[-1] == 'M':
                    Market_cap = float(Market_cap_str[:-1])

                    print('Market cap = ', str(Market_cap))
                else:
                    Market_cap = 0

                    print('Error in obtaining Market cap!')


    return Market_cap



def get_stockanalysis_ttm_income(ticker):
    financials_page = "https://stockanalysis.com/stocks/" + ticker + \
                 "/financials/trailing/"

    page = requests.get(financials_page,headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    page_content = page.content

    #parse the page
    soup = BeautifulSoup(page_content,'html.parser')

    try:
        tables = pd.read_html(page.text, attrs={'class': 'svelte-17fayh1'})
        tables_ok = True
    except(ValueError):
        tables_ok = False
        print("No ttm earnings tables found for " + ticker)

    if tables_ok:

        #get the first table which is the earnings estimates table
        income_table = tables[0]

        #drop last column
        income_table = income_table.iloc[:, :-1]

        #set the Breakdown column as an Index
        income_table.set_index("Quarter Ending", inplace = True)

        columns = list(income_table)

        #convert strings to numbers
        for i in columns:

            income_table[i] = convert_to_numeric(income_table[i])

    return income_table

def get_stockanalysis_ttm_balancesheet(ticker):
    selected_page = "https://stockanalysis.com/stocks/" + ticker + \
                 "/financials/balance-sheet/trailing/"

    page = requests.get(selected_page,headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    page_content = page.content

    #parse the page
    soup = BeautifulSoup(page_content,'html.parser')

    try:
        tables = pd.read_html(page.text, attrs={'class': 'svelte-17fayh1'})
        tables_ok = True
    except(ValueError):
        tables_ok = False
        print("No ttm balance sheet tables found for " + ticker)


    if tables_ok:

        #get the first table which is the earnings estimates table
        selected_table = tables[0]

        #drop last column
        selected_table = selected_table.iloc[:, :-1]

        #set the Breakdown column as an Index
        selected_table.set_index("Quarter Ending", inplace = True)

        columns = list(selected_table)

        #convert strings to numbers
        for i in columns:

           selected_table[i] = convert_to_numeric(selected_table[i])

        #fill NaN will '-'
        #final_table = cashflow_table.fillna('-')

        #print(selected_table)

        return selected_table
    else:
        return None


def get_stockanalysis_ttm_cashflow(ticker):
    cashflow_page = "https://stockanalysis.com/stocks/" + ticker + \
                 "/financials/cash-flow-statement/trailing/"

    page = requests.get(cashflow_page,headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    page_content = page.content

    #parse the page
    soup = BeautifulSoup(page_content,'html.parser')

    try:
        tables = pd.read_html(page.text, attrs={'class': 'svelte-17fayh1'})
        tables_ok = True
    except(ValueError):
        tables_ok = False
        print("No cash flow tables found for " + ticker)

    selected_table = None

    if tables_ok:

        #get the first table which is the earnings estimates table
        selected_table = tables[0]


        #drop last column
        selected_table = selected_table.iloc[:, :-1]

        #set the Breakdown column as an Index
        selected_table.set_index("Quarter Ending", inplace = True)

        columns = list(selected_table)

        #convert strings to numbers
        for i in columns:

           selected_table[i] = convert_to_numeric(selected_table[i])

        #fill NaN will '-'
        #final_table = cashflow_table.fillna('-')

        #print(selected_table)

    return selected_table


def get_nbc_yieldQuote(ticker):

    ticker = 'US30Y'

    #get cash flow data
    url = "https://cnbc.com/quotes/" + ticker

    r = requests.get(url,headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    #driver.find_element_by_xpath("//button[@data-reactid = '36']").click()

    #get the button with class id expandPf button
    #driver.find_element_by_css_selector('.expandPf').click()

    content = r.content

    #parse the page
    page_soup = BeautifulSoup(content,'html.parser')

    #features = cashflow_soup.find_all('div', {'class': ['D(tbr)','D(ib)']})

    data = page_soup.find('span', class_='QuoteStrip-lastPrice')

    last_ValuePercent = round(float(data.text[:-1])/100,4)

    print('Latest Yield = ', last_ValuePercent)

    return last_ValuePercent


#get latest bond yield from YCharts
def get_ycharts_yield_quote(ticker):

    #ticker = 'us_corporate_a_effective_yield'

    #get URL
    url = "https://ycharts.com/indicators/" + ticker

    r = requests.get(url,headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    try:
        tables = pd.read_html(r.text, match='Last Value')
        tables_ok = True
    except(ValueError):
        tables_ok = False
        print("No last value table found for " + ticker)

    if tables_ok:

        df = tables[0]

        last_Value = df.loc[0][1]

        #data = page_soup.find('span', class_='QuoteStrip-lastPrice')

        last_ValuePercent = round(float(last_Value[:-1])/100,4)

        print('Latest Yield = ', last_ValuePercent)

        return last_ValuePercent

    else:
        return 0


#calculates cost of equity to be displayed on Django Form and used for further calculations
#CRP - Country Risk Premium from Django form input
#CSRP - Company Risk Premium from Django form input
def calculate_costOfEquity(ticker,CRP, CSRP):

    Risk_free_rate = get_nbc_yieldQuote('US30Y')

    #print('The current US 30 years treasury yield = ', Risk_free_rate)

    ERP = 0.1

    #Store in DB - Beta
    Beta = get_yahoo_beta(ticker)

    #Ke is the final result to be displyed in Django "Cost of Equity"
    #Display in %: Ke * 100
    #Store in DB - Ke
    Ke = Risk_free_rate + (Beta * ERP) + CSRP + CRP

    print('Cost of Equity = ', Ke)

    #Return Cost of Equity = Ke
    return Ke

#function to calculate cost of debt
#ticker is from the Symbol field
#rating is from the rating field
def calculate_costOfDebt(ticker, rating, premium):

    Risk_free_rate = get_nbc_yieldQuote('US30Y')

    #Get this from Django form - "Rating" field
    Rating = rating.lower()

    Rating = 'aaa'

    #Use A rating as the average rating of S&P500 companies
    #CorporateYield = get_ycharts_yield_quote('us_corporate_a_effective_yield')

    if (Rating == 'aaa'):
        CorporateYield = get_ycharts_yield_quote('us_coporate_'+Rating+'_effective_yield')
    if (CorporateYield == 0 or Rating == 'aa' or Rating == 'a' or Rating == 'bbb'):
        CorporateYield = get_ycharts_yield_quote('us_corporate_'+Rating+'_effective_yield')
    else:
        if (Rating == 'bb' or Rating == 'b' or Rating == 'ccc'):
            CorporateYield = get_ycharts_yield_quote('us_high_yield_'+Rating+'_effective_yield')

    print(CorporateYield)

    if (CorporateYield >= 0):

        Default_spread = CorporateYield - Risk_free_rate

        print('Default Spread = ', Default_spread)

    else:

        Default_spread = Risk_free_rate

    print('Default Spread = ', Default_spread)

    #Store in DB - Kd
    Kd = Risk_free_rate + Default_spread + premium

    print('Cost of debt = ', Kd)

    #return Cost of Debt = Kd
    return Kd


def get_DCF_equity_value(ticker, WACC, NOPAT, Growth_rate, Net_debt, ROC):

    Equity_value = round(random.uniform(1000,10000),2)

    print('Equity value = ', Equity_value)

    return Equity_value

#when the user submits the form - this function will run to get the perpetual growth rate
def estimate_growth_rate(ticker,CRP,CSRP,rating,premium):

    todayDate = date.today()
    #Store in DB - Date
    todayDate_dMY = todayDate.strftime("%d-%b-%Y")

    #Store in DB - Symbol Name
    SymbolName = get_symbol_name(ticker)

    #Store in DB - Currency
    SymbolCurrency = get_symbol_currency(ticker)

    print(SymbolName + ' '+ SymbolCurrency)

    income_df = get_stockanalysis_ttm_income(ticker)

    cashflow_df = get_stockanalysis_ttm_cashflow(ticker)

    balancesheet_df = get_stockanalysis_ttm_balancesheet(ticker)

    #0 - is ttm column
    column_used = 0

    #Store in DB - Revenue TTM
    Revenue_latest = income_df.loc['Revenue'][column_used]

    EBITDA_latest = income_df.loc['EBITDA'][column_used]

    EBIT_latest = income_df.loc['EBIT'][column_used]

    PBT_latest = income_df.loc['Pretax Income'][column_used]

    Taxes_latest = income_df.loc['Income Tax'][column_used]

    try:
        Depreciation_latest = cashflow_df.loc['Depreciation & Amortization'][column_used]

    except KeyError:
        Depreciation_latest = 0

    #if EBIT is NaN or less than zero then this method is not suitable
    if (math.isnan(EBIT_latest) or (EBIT_latest <= 0)):
        print('EBIT is less than or equal to ZERO. No value can be calculated.')
        #return np.nan

    Tax_rate = Taxes_latest / PBT_latest
    Tax_rate_percent = f"{Tax_rate:.1%}"
    print(Tax_rate_percent)

    #Store in DB - NOP TTM
    Net_Operating_Income = round(EBIT_latest * (1 - Tax_rate),0)

    cashflow_df = get_stockanalysis_ttm_cashflow(ticker)

    try:
        Capex = cashflow_df.loc['Capital Expenditures'][column_used]
    except KeyError:
        Capex = 0

    try:
        Acquisitions = cashflow_df.loc['Acquisitions'][column_used]
    except KeyError:
        Acquisitions = 0

    Working_capital_changes = cashflow_df.loc['Other Operating Activities'][column_used]

    Reinvestment = Capex + Acquisitions + Depreciation_latest + Working_capital_changes

    print('Capex = ',Capex)
    print('Acquisitions = ', Acquisitions)
    print('WC changes = ', Working_capital_changes)
    print('Reinvestment = ', Reinvestment)

    try:
        Goodwill = balancesheet_df.loc['Goodwill and Intangibles'][column_used]
    except KeyError:
        Goodwill = 0

    print('Goodwill = ', Goodwill)

    Total_debt = balancesheet_df.loc['Total Debt'][column_used]

    Total_cash_equivalents = balancesheet_df.loc['Cash & Cash Equivalents'][column_used]

    print('Total Debt = ', Total_debt)

    print('Total Cash = ', Total_cash_equivalents)

    Net_debt = Total_debt - Total_cash_equivalents

    print('Net debt = ', Net_debt)

    Equity_BV = balancesheet_df.loc["Shareholders' Equity"][column_used]

    print("Shareholders' equity = ", Equity_BV)

    Invested_capital = Total_debt + Equity_BV

    print('Invested capital = ', Invested_capital)

    Net_income_common = income_df.loc['Net Income Common'][column_used]

    #Store in DB - ROE
    ROE = Net_income_common / Equity_BV

    print('ROE = ', f"{ROE:.1%}")

    #Store in DB - ROC
    ROC = Net_Operating_Income / Invested_capital

    print('ROC = ', f"{ROC:.1%}")

    Ke = calculate_costOfEquity(ticker,CRP,CSRP)

    print('Cost of Equity = ', Ke)

    Kd = calculate_costOfDebt(ticker, rating, premium)

    print('Cost of debt = ', Kd)

    #Store in DB - DE Ratio
    DE_ratio = Total_debt /Equity_BV

    print('D/E Ratio = ', DE_ratio)

    Debt_percent = DE_ratio / (DE_ratio + 1)

    print('Debt percent = ', f"{Debt_percent:.1%}")

    #Store in DB - WACC
    WACC = (Kd * Debt_percent) + (Ke * (1 - Debt_percent))

    #print('WACC = ', WACC)

    #print('Net Operating Income = ', Net_Operating_Income)

    #placeholder
    Growth_rate = 0.03

    #Store in DB - Market Cap
    Market_cap = get_yahoo_marketcap(ticker)

    #Store in DB - EV
    Actual_EV = Market_cap + Net_debt

    #Store in DB - Perpetual Growth Rate
    Perpetual_Growth_Rate = round(random.uniform(Growth_rate-0.02,Growth_rate+0.01),4)

    print('Perpetual Growth rate = ', Perpetual_Growth_Rate)

    return Perpetual_Growth_Rate


estimate_growth_rate('AAPL', 0, 0.05, 'aaa',0.01)