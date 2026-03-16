import time, datetime, traceback, sys
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from xtquant import xtconstant
import logging
from model import model
from model.model import singleton
from core import PositionManager
from config.config import exec_config

logger = logging.getLogger(__name__)

@singleton
class XTExecution(XtQuantTraderCallback):
    def __init__(self, path: str, account: str):
        super().__init__()
        session_id = int(time.time())
        self.api = XtQuantTrader(path, session_id)
        self.account = StockAccount(account, 'STOCK')
        self.orders = {}
        self.api.register_callback(self)
        self.api.start()
        ret = self.api.connect()
        if ret == 0:
            logger.info("XTExecution Start Success")
        else:
            logger.fatal("XTExecution Start Failed")

        ret = self.api.subscribe(self.account)
        if ret == 0:
            logger.info("XTExecution Subscribe trading Success")
        else:
            logger.fatal("XTExecution Subscribe trading Failed")

    def ReqInsertOrder(self, order: model.Order) -> int:
        side = xtconstant.STOCK_BUY if order.order_side == model.OrderSide.BUY else xtconstant.STOCK_SELL
        ret = self.api.order_stock_async(self.account, order.stock_code, side, order.input_vol
                                               , xtconstant.FIX_PRICE, order.input_px, order.algo_id, order.order_id)
        if ret > 0 :
            logger.info("ReqInsertOrder success order_id: %s, account: %s, stock_code: %s", order.order_id, self.account.account_id, order.stock_code)
            self.orders[order.order_id] = order
        else:
            logger.error("ReqInsertOrder failed order_id: %s, account: %s, stock_code: %s", order.order_id, self.account.account_id, order.stock_code)
        return ret
        
    def ReqCancelOrder(self, order_id: str) -> int:
        if order_id not in self.orders:
            logger.error("ReqCancelOrder failed order_id: %s, account: %s, stock_code: %s, not found order", order_id, self.account.account_id)
            return -1
        order = self.orders[order_id]
        market = xtconstant.SH_MARKET if order.market == "SH" else xtconstant.SZ_MARKET
        if len(order.order_sys_id) == 0:
            logger.error("ReqCancelOrder failed order_id: %s, account: %s, stock_code: %s, not found order_sys_id", order.order_id, self.account.account_id, order.stock_code)
            return -1
        ret = self.api.cancel_order_stock_sysid_async(self.account, market, order.order_sys_id)
        if ret > 0 :
            logger.info("ReqCancelOrder success order_id: %s, account: %s, stock_code: %s", order.order_id, self.account.account_id, order.stock_code)
        else:
            logger.error("ReqCancelOrder failed order_id: %s, account: %s, stock_code: %s", order.order_id, self.account.account_id, order.stock_code)
        return ret
    
    def GetOrderByOrderID(self, order_id: str) -> model.Order:
        if order_id in self.orders:
            return self.orders[order_id]
        logger.error("GetOrderByOrderID error, not found order_id: %s", order_id)
        return None
    
    def on_disconnected(self):
        """
        连接断开
        :return:
        """
        logger.error('XTExecution disconnected ', datetime.datetime.now())

    def on_stock_order(self, order):
        """
        委托回报推送
        :param order: XtOrder对象
        :return:
        """
        status = ""
        if order.order_status in model.xt_status_map:
            status = model.status_string_map[model.xt_status_map[order.order_status].value]
        logger.info('XTExecution on_stock_order order_id: %s, account: %s, stock_code: %s, order_status: %s'
                    , order.order_remark, order.account_id, order.stock_code, status)
        norder = model.Order(order.stock_code, order.order_volume, order.price, order_id=order.order_remark)
        norder.order_status = model.xt_status_map[order.order_status]
        norder.order_sys_id = order.order_sysid
        norder.filled_vol = order.traded_volume
        norder.filled_px = order.traded_price
        self.update_order(norder)

    def on_stock_trade(self, trade):
        """
        成交变动推送
        :param trade: XtTrade对象
        :return:
        """
        print(datetime.datetime.now(), '成交回调', trade.order_remark, f"委托方向(48买 49卖) {trade.offset_flag} 成交价格 {trade.traded_price} 成交数量 {trade.traded_volume}")

    def on_order_error(self, order_error):
        """
        委托失败推送
        :param order_error:XtOrderError 对象
        :return:
        """
        # print("on order_error callback")
        # print(order_error.order_id, order_error.error_id, order_error.error_msg)
        logger.error("on_order_error order_id: %s, msg: %s", {order_error.order_remark}, {order_error.error_msg})

    def on_cancel_error(self, cancel_error):
        """
        撤单失败推送
        :param cancel_error: XtCancelError 对象
        :return:
        """
        print(datetime.datetime.now(), sys._getframe().f_code.co_name)

    def on_order_stock_async_response(self, response):
        """
        异步下单回报推送
        :param response: XtOrderResponse 对象
        :return:
        """
        status = ""
        if response.order_status in model.xt_status_map:
            status = model.status_string_map[model.xt_status_map[response.order_status].value]
        logger.info('XTExecution on_stock_order order_id: %s, account: %s, stock_code: %s, order_status: %s'
                    , response.order_remark, response.account_id, response.stock_code, status)
        # order = model.Order(response.stock_code, response.order_volume, response.price, order_id=response.order_remark)
        # order.order_status = model.xt_status_map[response.order_status]
        # order.order_sys_id = response.order_sysid
        # order.filled_vol = response.traded_volume
        # order.filled_px = response.traded_price
        # self.update_order(order)

    def on_cancel_order_stock_async_response(self, response):
        """
        :param response: XtCancelOrderResponse 对象
        :return:
        """
        print(datetime.datetime.now(), sys._getframe().f_code.co_name)

    def on_account_status(self, status):
        """
        :param response: XtAccountStatus 对象
        :return:
        """
        print(datetime.datetime.now(), sys._getframe().f_code.co_name)

    def update_order(self, order: model.Order):
        if order.order_id in self.orders:
            cache_order = self.orders[order.order_id]
            if len(cache_order.order_sys_id) == 0:
                cache_order.order_sys_id = order.order_sys_id
            if order.order_status.value > cache_order.order_status.value or (order.order_status == cache_order.order_status and order.filled_vol > cache_order.filled_vol):
                cache_order.order_status = order.order_status
                cache_order.partial_vol = order.filled_vol - cache_order.filled_vol
                cache_order.partial_px = 0 if cache_order.partial_vol == 0 else (order.filled_vol * order.filled_px - cache_order.filled_vol * cache_order.filled_px) / cache_order.partial_vol
                cache_order.filled_vol = order.filled_vol
                cache_order.filled_px = order.filled_px
                cache_order.update_time = order.update_time
                self.orders[order.order_id] = cache_order
                PositionManager.position_instance.update_position(cache_order)
                logger.info("update_order order_id: %s, stock_code: %s, filled_vol: %d, filled_px: %f, partial_vol: %d, partial_px: %f"
                            , order.order_id, cache_order.stock_code, cache_order.filled_vol, cache_order.filled_px, cache_order.partial_vol, cache_order.partial_px)
        else:
            self.orders[order.order_id] = order

xt_trader = XTExecution(exec_config['path'], exec_config['account_id'])