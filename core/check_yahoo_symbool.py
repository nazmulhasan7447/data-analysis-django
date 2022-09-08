# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 17:39:00 2022

@author: henryong
"""

import yahoo_fin.stock_info as si

symbol_ok = False

# symbol should be from the Django form - Symbol field
# 'AAPL' is just a placeholder
# symbol = 'msft'


# aapl

# function to check if symbol is found
# returns symbol_ok is True if a correct symbol is found
def symbol_found(symbol):
    try:
        # returns data of dictionary type
        data = si.get_quote_data(symbol)

        # exchange must be NY stock exhcange or Nasdaq
        if (data["exchange"] == "NYQ" or data["exchange"] == "NMS"):
            symbol_ok = True

        else:
            # symbol found but not from exchanges covered
            symbol_ok = False  # set symbol_ok to False
        return symbol_ok
    except:
        return False
    # if symbol is not found then IndexError is handled

