"""
DCF Valuation of public listed stocks
first created on 26 May 2022
updated 22 Sep 2022

"""
import datetime
import random

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import date
import math
from lxml import html
import time
import yahoo_fin.stock_info as si

pd.options.mode.chained_assignment = None  # default='warn'

# set the number of columns to display
pd.set_option('display.max_columns', 8)


# set the number of columns to display
pd.set_option('display.max_columns', 8)

# function to check if symbol is found
# returns symbol_ok is True if a correct symbol is found
def symbol_found(symbol):
    symbol_ok = False

    try:
        # returns data of dictionary type
        data = si.get_quote_data(symbol)
        symbol_name = data['shortName']

        # exchange must be NY stock exhcange or Nasdaq
        if (data["exchange"] == "NYQ" or data["exchange"] == "NMS"):
            symbol_ok = True
        else:
            # symbol found but not from exchanges covered
            symbol_ok = False  # set symbol_ok to False

        return symbol_ok

    # if symbol is not found then IndexError is handled
    except(IndexError):
        symbol_ok = False  # set symbol_ok to False
        return symbol_ok

#get symbol name
def get_symbol_name(ticker):
    # Symbol Name - to be store in DB
    symbol_name = ''

    try:
        # returns data of dictionary type
        data = si.get_quote_data(ticker)

        # exchange must be NY stock exhcange or Nasdaq
        if (symbol_found(ticker)):
            symbol_name = data['shortName']
        else:
            # symbol found but not from exchanges covered
            symbol_name = "Error"

        return symbol_name

    # if symbol is not found then IndexError is handled
    except(IndexError):
        symbol_name = "Error!"  # set error
        return symbol_name

#get symbol currency from yahoo
def get_symbol_currency(ticker):
    symbol_name = ''

    try:
        # returns data of dictionary type
        data = si.get_quote_data(ticker)

        # exchange must be NY stock exhcange or Nasdaq
        if (symbol_found(ticker)):
            symbol_currency = data['currency']
        else:
            # symbol found but not from exchanges covered
            symbol_currency = "Error!"

        return symbol_currency

    # if symbol is not found then IndexError is handled
    except(IndexError):
        symbol_currency = "Error!"  # set error
        return symbol_currency

# function to make all values numerical
def convert_to_numeric(column):
    first_col = [i.replace(',', '') for i in column]
    # second_col = [i.replace('-','') if i.value =='-' for i in first_col ]
    second_col = []
    for i in first_col:
        if (len(i) > 1):
            second_col.append(i)
        else:
            second_col.append(i.replace('-', ''))

    third_col = [i.replace('%', '') for i in second_col]
    final_col = pd.to_numeric(third_col)

    return final_col

def get_yahoo_Stock_Summary(ticker):
    quote_page = 'http://finance.yahoo.com/quote/' + ticker

    # get the tag with the provided class name
    # name_box = soup.find('h1',attrs={'class':'D(ib) Fz(18px)'})

    # get the text without the tags
    # name = name_box.text.strip()

    page = requests.get(quote_page, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    page_content = page.content

    # parse the page
    soup = BeautifulSoup(page_content, 'lxml')

    features = soup.find_all('div', id_='Main')

    # get the tag with the provided class name
    # name_box = soup.find('h1',attrs={'class':'D(ib) Fz(18px)'})

    headers = []
    temp_list = []
    label_list = []
    final = []
    index = 0
    # create headers
    for item in features[0].find_all('div', class_='D(ib)'):
        headers.append(item.text)
    # statement contents
    while index <= len(features) - 1:
        # filter for each line of the statement
        temp = features[index].find_all('div', class_='D(tbc)')
        for line in temp:
            # each item adding to a temporary list
            temp_list.append(line.text)
        # temp_list added to final list
        final.append(temp_list)
        # clear temp_list
        temp_list = []
        index += 1
    df = pd.DataFrame(final[1:])
    df.columns = headers

    # convert strings to numbers
    for column in headers[1:]:
        df[column] = convert_to_numeric(df[column])

    print(df)

    # fill NaN will '-'
    # final_df = df.fillna('-')

    # get the text without the tags
    # name = name_box.text.strip()

    # set the Breakdown column as an Index
    # final_df.set_index("Breakdown", inplace = True)

    return df


def get_yahoo_beta(ticker):
    # the page to scrape
    analysis_page = "https://finance.yahoo.com/quote/" + ticker + \
                    "/key-statistics?p=" + ticker

    r = requests.get(analysis_page, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    # print(r)

    # read the tables in the given page
    try:
        tables = pd.read_html(r.text)
        tables_ok = True
    except(ValueError):
        tables_ok = False

    # print(tables)

    if tables_ok:
        # get the tables that are 5 columns only and get rid of the others
        # tables = [table for table in tables if table.shape[1] == 5]

        # get the second table which is the stock history table
        selected_table = tables[1]

        Beta = float(selected_table.iloc[0, 1])

        if (math.isnan(Beta) == False):
            return Beta
        else:
            Beta = 1
            return Beta

    else:

        Beta = 1
        return Beta


def get_stockanalysis_ttm_income(ticker):
    financials_page = "https://stockanalysis.com/stocks/" + ticker + \
                      "/financials/trailing/"

    page = requests.get(financials_page, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    page_content = page.content

    # parse the page
    soup = BeautifulSoup(page_content, 'html.parser')

    try:
        tables = pd.read_html(page.text, attrs={'class': 'svelte-17fayh1'})
        tables_ok = True
    except(ValueError):
        tables_ok = False

    if tables_ok:

        # get the first table which is the earnings estimates table
        income_table = tables[0]

        # drop last column
        income_table = income_table.iloc[:, :-1]

        # set the Breakdown column as an Index
        income_table.set_index("Quarter Ending", inplace=True)

        columns = list(income_table)

        # convert strings to numbers
        for i in columns:
            income_table[i] = convert_to_numeric(income_table[i])

        # fill NaN will '-' take this away because - wil take away negative values
        # final_income_table = income_table.fillna('-')

        # print(income_table)

    return income_table


def get_stockanalysis_ttm_balancesheet(ticker):
    selected_page = "https://stockanalysis.com/stocks/" + ticker + \
                    "/financials/balance-sheet/trailing/"

    page = requests.get(selected_page, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    page_content = page.content

    # parse the page
    soup = BeautifulSoup(page_content, 'html.parser')

    try:
        tables = pd.read_html(page.text, attrs={'class': 'svelte-17fayh1'})
        tables_ok = True
    except(ValueError):
        tables_ok = False

    if tables_ok:

        # get the first table which is the earnings estimates table
        selected_table = tables[0]

        # drop last column
        selected_table = selected_table.iloc[:, :-1]

        # set the Breakdown column as an Index
        selected_table.set_index("Quarter Ending", inplace=True)

        columns = list(selected_table)

        # convert strings to numbers
        for i in columns:
            selected_table[i] = convert_to_numeric(selected_table[i])

        # fill NaN will '-'
        # final_table = cashflow_table.fillna('-')

        # print(selected_table)

    return selected_table


def get_stockanalysis_ttm_cashflow(ticker):
    cashflow_page = "https://stockanalysis.com/stocks/" + ticker + \
                    "/financials/cash-flow-statement/trailing/"

    page = requests.get(cashflow_page, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    page_content = page.content

    # parse the page
    soup = BeautifulSoup(page_content, 'html.parser')

    try:
        tables = pd.read_html(page.text, attrs={'class': 'svelte-17fayh1'})
        tables_ok = True
    except(ValueError):
        tables_ok = False

    if tables_ok:

        # get the first table which is the earnings estimates table
        selected_table = tables[0]

        # drop last column
        selected_table = selected_table.iloc[:, :-1]

        # set the Breakdown column as an Index
        selected_table.set_index("Quarter Ending", inplace=True)

        columns = list(selected_table)

        # convert strings to numbers
        for i in columns:
            selected_table[i] = convert_to_numeric(selected_table[i])

    return selected_table


#get risk free rate from NBC
def get_nbc_yieldQuote(ticker):
    ticker = 'US30Y'

    # get cash flow data
    url = "https://cnbc.com/quotes/" + ticker

    r = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    # driver.find_element_by_xpath("//button[@data-reactid = '36']").click()

    # get the button with class id expandPf button
    # driver.find_element_by_css_selector('.expandPf').click()

    content = r.content

    # parse the page
    page_soup = BeautifulSoup(content, 'html.parser')

    # features = cashflow_soup.find_all('div', {'class': ['D(tbr)','D(ib)']})

    data = page_soup.find('span', class_='QuoteStrip-lastPrice')

    last_ValuePercent = round(float(data.text[:-1]) / 100, 4)

    return last_ValuePercent

# calculates cost of equity to be displayed on Django Form and used for further calculations
# CRP - Country Risk Premium from Django form input
# CSRP - Company Risk Premium from Django form input
def calculate_costOfEquity(ticker, CRP, CSRP):
    Risk_free_rate = get_nbc_yieldQuote('US30Y')

    # print('The current US 30 years treasury yield = ', Risk_free_rate)

    ERP = 0.1

    # Store in DB - Beta
    Beta = get_yahoo_beta(ticker)

    # Ke is the final result to be displyed in Django "Cost of Equity"
    # Display in %: Ke * 100
    # Store in DB - Ke
    Ke = round((Risk_free_rate + (Beta * ERP) + CSRP + CRP) * 100, 2)

    # Return Cost of Equity = Ke
    return Ke

# get latest bond yield from YCharts
def get_ycharts_yield_quote(ticker):
    # ticker = 'us_corporate_a_effective_yield'

    # get URL
    url = "https://ycharts.com/indicators/" + ticker

    r = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    try:
        tables = pd.read_html(r.text, match='Last Value')
        tables_ok = True
    except(ValueError):
        tables_ok = False
        print("No last value table found for " + ticker)

    if tables_ok:

        df = tables[0]

        last_Value = df.loc[0][1]

        # data = page_soup.find('span', class_='QuoteStrip-lastPrice')

        last_ValuePercent = round(float(last_Value[:-1]) / 100, 4)

        print('Latest Yield = ', last_ValuePercent)

        return last_ValuePercent

    else:
        return 0


# function to calculate cost of debt
# ticker is from the Symbol field
# rating is from the rating field

def calculate_costOfDebt(ticker, rating, premium):

    Risk_free_rate = get_nbc_yieldQuote('US30Y')

    # Get this from Django form - "Rating" field
    Rating = rating.lower()

    # Use A rating as the average rating of S&P500 companies
    # CorporateYield = get_ycharts_yield_quote('us_corporate_a_effective_yield')

    if Rating == 'aaa':
        CorporateYield = get_ycharts_yield_quote('us_coporate_' + Rating + '_effective_yield')
    if CorporateYield == 0 or Rating == 'aa' or Rating == 'a' or Rating == 'bbb':
        CorporateYield = get_ycharts_yield_quote('us_corporate_' + Rating + '_effective_yield')
    else:
        if Rating == 'bb' or Rating == 'b' or Rating == 'ccc':
            CorporateYield = get_ycharts_yield_quote('us_high_yield_' + Rating + '_effective_yield')

    if CorporateYield >= 0:
        Default_spread = CorporateYield - Risk_free_rate

    else:
        Default_spread = Risk_free_rate

    # Store in DB - Kd
    Kd = round((Risk_free_rate + Default_spread + premium) * 100, 2)

    return Kd

def get_yahoo_marketcap(ticker):
    print("Getting market cap for " + ticker)

    # the page to scrape
    analysis_page = "https://finance.yahoo.com/quote/" + ticker + \
                    "/key-statistics?p=" + ticker

    r = requests.get(analysis_page, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    # print(r)

    # read the tables in the given page
    try:
        tables = pd.read_html(r.text)
        tables_ok = True
    except(ValueError):
        tables_ok = False
        print("No statistics tables found for " + ticker)

    # print(tables)

    if tables_ok:
        # get the tables that are 5 columns only and get rid of the others
        # tables = [table for table in tables if table.shape[1] == 5]

        # get the second table which is the stock history table
        selected_table = tables[0]

        print(selected_table)

        Market_cap_str = (selected_table.iloc[0, 1])

        # convert market cap to millions
        if Market_cap_str[-1] == 'T':
            Market_cap = float(Market_cap_str[:-1])

            Market_cap = Market_cap * 1000000  # convert to millions

            print('Market cap = ', str(Market_cap))

        else:
            if Market_cap_str[-1] == 'B':
                Market_cap = float(Market_cap_str[:-1])

                Market_cap = Market_cap * 1000  # convert to millions

                print('Market cap = ', str(Market_cap))
            else:
                if Market_cap_str[-1] == 'M':
                    Market_cap = float(Market_cap_str[:-1])

                    print('Market cap = ', str(Market_cap))
                else:
                    Market_cap = 0

                    print('Error in obtaining Market cap!')

    return Market_cap

# to EV and equity value using FCFF DCF method
#TODO Changed label are requries changing
def get_3_stage_growth_value(ticker, CRP,CSRP,rating,premium,Stage1_years,Stage1_growthRate,Stage2_years,Stage2_growthRate,perpetual_growthRate):

    todayDate = date.today()
    # Store in DB - Date
    todayDate_dMY = todayDate.strftime("%d-%b-%Y")

    # Store in DB - Symbol Name
    SymbolName = get_symbol_name(ticker)

    # Store in DB - Currency
    SymbolCurrency = get_symbol_currency(ticker)

    income_df = get_stockanalysis_ttm_income(ticker)

    cashflow_df = get_stockanalysis_ttm_cashflow(ticker)

    balancesheet_df = get_stockanalysis_ttm_balancesheet(ticker)

    # 0 - is ttm column
    column_used = 0

    # Store in DB - Revenue TTM
    Revenue_latest = income_df.loc['Revenue'][column_used]

    EBITDA_latest = income_df.loc['EBITDA'][column_used]

    EBIT_latest = income_df.loc['EBIT'][column_used]

    PBT_latest = income_df.loc['Pretax Income'][column_used]

    Taxes_latest = income_df.loc['Income Tax'][column_used]

    Depreciation_latest = cashflow_df.loc['Depreciation & Amortization'][column_used]

    # if the there is no value for ttm EBTIDA then try to get the latest FY
    if (math.isnan(EBITDA_latest) or math.isnan(PBT_latest) or math.isnan(Taxes_latest)):
        column_used = 1  # move from ttm or next latest financial period
        EBITDA_latest = income_df.loc['Normalized EBITDA'][column_used]
        PBT_latest = income_df.loc['Pretax Income'][column_used]
        Taxes_latest = income_df.loc['Tax Provision'][column_used]

    # if EBITDA is NaN or less than zero then this method is not suitable
    if (math.isnan(EBITDA_latest) or (EBITDA_latest <= 0)):
        print('EBITDA is less than or equal to ZERO. No value can be calculated.')
        # return np.nan

    # if EBIT is NaN or less than zero then this method is not suitable
    if (math.isnan(EBIT_latest) or (EBIT_latest <= 0)):
        print('EBIT is less than or equal to ZERO. No value can be calculated.')
        # return np.nan

    Tax_rate = Taxes_latest / PBT_latest
    Tax_rate_percent = f"{Tax_rate:.1%}"

    EBITDA_margin_ttm = EBITDA_latest / Revenue_latest
    EBITDA_margin_ttm_percent = f"{EBITDA_margin_ttm:.1%}"


    # Store in DB - NOP TTM
    Net_Operating_Income = round(EBIT_latest * (1 - Tax_rate), 0)


    cashflow_df = get_stockanalysis_ttm_cashflow(ticker)


    # Calculate reinvestment
    Capex = cashflow_df.loc['Capital Expenditures'][column_used]

    Acquisitions = cashflow_df.loc['Acquisitions'][column_used]

    Working_capital_changes = cashflow_df.loc['Other Operating Activities'][column_used]

    Reinvestment = Capex + Acquisitions + Depreciation_latest + Working_capital_changes

    Goodwill = balancesheet_df.loc['Goodwill and Intangibles'][column_used]

    # Current_debt = balancesheet_df.loc['Current Debt'][column_used]

    # Longterm_debt = balancesheet_df.loc['Long-Term Debt'][column_used]

    Total_debt = balancesheet_df.loc['Total Debt'][column_used]

    Total_cash_equivalents = balancesheet_df.loc['Cash & Cash Equivalents'][column_used]

    Net_debt = Total_debt - Total_cash_equivalents

    Equity_BV = balancesheet_df.loc["Shareholders' Equity"][column_used]

    Invested_capital = Total_debt + Equity_BV

    Net_income_common = income_df.loc['Net Income Common'][column_used]

    # Store in DB - ROE
    ROE = (Net_income_common / Invested_capital) * 100

    # Store in DB - ROC
    ROC = (Net_Operating_Income / Equity_BV) * 100


    # Store in DB - Stage 1 (Yrs)
    First_stage_years = Stage1_years

    # Store in DB - Stage 1 Growth
    First_stage_growth_rate = Stage1_growthRate * 100

    # Store in DB - Stage 2 (Yrs)
    Second_stage_years = Stage2_years

    # Store in DB - Stage 2 Growth
    Second_stage_growth_rate = Stage2_growthRate * 100

    # Store in DB - Perpetual Growth
    Growth_rate = perpetual_growthRate * 100

    # first stage reinvestment rate
    First_stage_reinvestment_rate = First_stage_growth_rate / ROC


    # second stage reinvestment rate
    Second_stage_reinvestment_rate = Second_stage_growth_rate / ROE

    # long term reinvestment rate
    Reinvestment_rate = Growth_rate / ROE

    Risk_free_rate = get_nbc_yieldQuote('US30Y')

    ERP = random.uniform(0.04, 0.07)

    Beta = round(random.uniform(0.1, 2), 2)


    Ke = calculate_costOfEquity(ticker, CRP, CSRP)

    # Default_spread = float(input('Enter Default Spread = '))

    Kd = calculate_costOfDebt(ticker, rating, premium)

    if (Total_debt > 0):
        DE_ratio = round((Total_debt / Equity_BV) * 100, 2)
    else:
        DE_ratio = 0

    Debt_percent = DE_ratio / (DE_ratio + 1)


    WACC = round((Kd * Debt_percent) + (Ke * (1 - Debt_percent)), 2)


    Unlevered_beta = Beta / ((1 + (1 - Tax_rate) * DE_ratio))

    Kc = Risk_free_rate + Unlevered_beta * ERP

    #Changed
    FCFF1 = Net_Operating_Income * (1 + First_stage_growth_rate) * (1 - 0.1)

    #Changed
    First_stage_value = FCFF1 / WACC


    #Changed
    # get second stage starting FCFF
    Net_Operating_Income2 = Net_Operating_Income


    #Changed
    FCFF2 = Net_Operating_Income2 * (1 - Second_stage_reinvestment_rate)

    # FCFF2 = FCFF1 * (1 + First_stage_growth_rate)**(First_stage_years)*(1+Second_stage_growth_rate)


    Second_stage_growth_value = ((1 + Second_stage_growth_rate) / (1 + WACC))

    #Changed
    Second_stage_value = FCFF2 / ((1 + WACC) ** First_stage_years)


    Net_Operating_Income3 = Net_Operating_Income2


    #Changed
    FCFF3 = Net_Operating_Income3 * (1 - Reinvestment_rate)


    #Changed
    Third_stage_value = FCFF3 / ((WACC - Growth_rate) * (1 + WACC) ** (5))


    Enterprise_value = First_stage_value + Second_stage_value + Third_stage_value

    # Store in DB - Market Cap
    Market_cap = get_yahoo_marketcap(ticker)

    # Store in DB - EV
    Actual_EV = Market_cap + Net_debt

    #Store DB - intrinsic value
    Equity_value = round(Enterprise_value - Net_debt, 2)

    data = {
        "date": todayDate_dMY,
        "symbol": ticker,
        "symbol_name": SymbolName,
        "stage_1_growth": First_stage_growth_rate,
        "stage_2_growth": Second_stage_growth_rate,
        "perpetual_growth": Growth_rate,
        "currency": SymbolCurrency,
        "revnue_ttm": Revenue_latest,
        "nop_ttm": Net_Operating_Income,
        "roe": ROE,
        "roc": ROC,
        "ke": Ke,
        "kd": Kd,
        "de": DE_ratio,
        "wacc": WACC,
        "beta": Beta,
        "market_cap": Market_cap,
        "ev": Actual_EV,
        "intrinsic_value": Equity_value,
    }

    return data


# get_3_stage_growth_value('AAPL',0.1,0.05,'aaa',0.01,3,0.1,5,0.02,0.01)
