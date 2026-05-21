'''
Author: Leo 
Date: 2026-03-13 20:58:50
LastEditors: Leo 
LastEditTime: 2026-03-16 17:00:48
Description: 

Copyright (c) 2026 by ${git_name_email}, All Rights Reserved. 
'''
def get_lots(stock_code: str) -> int:
    if stock_code.startswith('68'):
        return 200
    return 100

def get_market(stock_code: str) -> str:
    s = stock_code[0]
    if s == '6' or s == '5':
        return "SH"
    elif s == '0' or s == '3' or s == '1':
        return "SZ"

def get_stock_code_with_market(stock_code: str):
    if len(stock_code) > 6:
        return stock_code, get_market(stock_code)
    market = get_market(stock_code)
    return stock_code + '.' + market, market
    
def round_volume(stock_code: str, input_vol: int, min_vol: int = 0) -> int:
    base_size = min_vol if min_vol >= 100 else get_lots(stock_code)
    return input_vol // base_size * base_size