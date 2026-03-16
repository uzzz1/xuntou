'''
Author: HideInTower 1075277345@qq.com
Date: 2026-03-14 20:11:00
LastEditors: HideInTower 1075277345@qq.com
LastEditTime: 2026-03-16 17:29:42
Description: 

Copyright (c) 2026 by ${git_name_email}, All Rights Reserved. 
'''
from enum import Enum
from risk import base_risk
import uuid
import time

class OrderSide(Enum):
    BUY = 1
    SELL = -1
    
class OrderStatus(Enum):
    CREATED = 0
    NEW = 1
    PARTIAL = 2
    PENDINGCANCEL = 3
    FILLED = 4
    CANCELED = 5
    ERROR = 6

xt_status_map = {
    48 : OrderStatus.CREATED,
    49 : OrderStatus.CREATED,
    50 : OrderStatus.NEW,
    51 : OrderStatus.PENDINGCANCEL,
    52 : OrderStatus.PENDINGCANCEL,
    53 : OrderStatus.CANCELED,
    54 : OrderStatus.CANCELED,
    55 : OrderStatus.PARTIAL,
    56 : OrderStatus.FILLED,
    57 : OrderStatus.ERROR,
    255: OrderStatus.CREATED
}

status_string_map = ["待报","已报","部成","待撤","已成","已撤","废单"]

def get_order_id() -> str:
    return uuid.uuid4().hex[:24]

class Orderbook:
    def __init__(self, stock_code: str):
        self.stock_code, self.market = base_risk.get_stock_code_with_market(stock_code)
        self.ask_px = [0 for i in range(10)]
        self.bid_px = [0 for i in range(10)]
        self.ask_vol = [0 for i in range(10)]
        self.bid_vol = [0 for i in range(10)]
    
class Order:
    def __init__(self, stock_code: str, input_vol: int, input_px: float, side: OrderSide = OrderSide.BUY, order_id: str = "", algo_id: str = ""):
        self.order_id = get_order_id() if len(order_id) == 0 else order_id
        self.order_sys_id = ""
        self.stock_code, self.market = base_risk.get_stock_code_with_market(stock_code)
        self.order_side = side
        self.input_vol = base_risk.round_volume(stock_code, input_vol)
        self.input_px = input_px
        self.filled_vol = 0
        self.filled_px = 0
        self.order_status = OrderStatus.CREATED
        self.create_time = int(time.time() * 1000)
        self.update_time = self.create_time
        self.algo_id = algo_id
        self.partial_vol = 0
        self.partial_px = 0
        self.remark = ""
        self.msg = ""

    def IsFinish(self) -> bool:
        return self.order_status.value > OrderStatus.PENDINGCANCEL.value

class Position:
    def __init__(self, stock_code: str, input_vol: int, side: OrderSide):
        self.stock_code, self.market = base_risk.get_stock_code_with_market(stock_code)
        self.input_vol = base_risk.round_volume(stock_code, input_vol)
        self.side = side
        self.filled_vol = 0
        self.avg_px = 0
        self.remain_vol = self.input_vol
        self.min_vol = base_risk.get_lots(stock_code)
        self.orders = set()

    def IsFinish(self) -> bool:
        return self.input_vol - self.filled_vol < self.min_vol

def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance