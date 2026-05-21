'''
Author: Leo 
Date: 2026-03-13 20:53:21
LastEditors: Leo 
LastEditTime: 2026-05-08 14:33:12
Description: 

Copyright (c) 2026 by ${git_name_email}, All Rights Reserved. 
'''
from model import model
from model.model import singleton
from gateway import Execution
from risk import base_risk
import time
import random
import logging

logger = logging.getLogger(__name__)

@singleton
class PositionManager:
    def __init__(self):
        self.positions = {}

    def deal_position(self, position: model.Position):
        orderbook = model.Orderbook(position.stock_code) #需要改成从行情模块中获取
        if orderbook is not None:
            on_way_vol = 0 #计算在外挂单的量
            for order_id in position.orders:
                order = Execution.xt_trader.GetOrderByOrderID(order_id)
                if order is not None and not order.IsFinish():
                    on_way_vol += (order.input_vol - order.filled_vol)
            leave_vol = position.remain_vol - on_way_vol
            if leave_vol < position.min_vol:
                return
            trade_vol = base_risk.round_volume(position.stock_code, 0.2 * position.input_vol, position.min_vol) #每次挂总量的五分之一
            if trade_vol > leave_vol:
                trade_vol = leave_vol
            if trade_vol < position.min_vol:
                trade_vol = position.min_vol
            price = orderbook.bid_px[0]
            if position.side == model.OrderSide.SELL:
                price = orderbook.ask_px[0]
            order = model.Order(position.stock_code, trade_vol, price, position.side)
            ret = Execution.xt_trader.ReqInsertOrder(order)
            if ret > 0:
                position.orders.add(order.order_id)

    def insert_position(self, position: model.Position):
        if position.stock_code not in self.positions:
            self.positions[position.stock_code] = position

    def update_position(self, order: model.Order):
        if order.stock_code in self.positions:
            avg_px = self.positions[order.stock_code].avg_px
            filled_vol = self.positions[order.stock_code].filled_vol
            self.positions[order.stock_code].filled_vol += order.partial_vol
            self.positions[order.stock_code].remain_vol -= order.partial_vol
            self.positions[order.stock_code].avg_px = (avg_px * filled_vol + order.partial_vol * order.partial_px) / (filled_vol + order.partial_vol)

    def run(self):
        while True:
            finished = []
            for stock_code, position in self.positions.items():
                if position.IsFinish():
                    finished.append(stock_code)
                    continue
                self.deal_position(position)
            for stock_code in finished:
                position = self.positions.pop(stock_code)
                logger.info("Position Finished stock_code: %s, side: %d, input_vol: %d, filled_vol: %d, avg_px: %.2f"
                            , position.stock_code, position.side.value,position.input_vol, position.filled_vol, position.avg_px)
            time.sleep(random.randint(2, 4))

position_instance = PositionManager()