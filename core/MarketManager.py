'''
Author: Leo 
Date: 2026-03-16 17:41:03
LastEditors: Leo 
LastEditTime: 2026-05-21 10:38:30
Description: 

Copyright (c) 2026 by ${git_name_email}, All Rights Reserved. 
'''
from model import model
from model.model import singleton, Orderbook
from gateway.Market import xt_market

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

@singleton
class MarketManager:
    def __init__(self):
        self.orderbooks: Dict[str, Orderbook] = {}  # symbol -> Orderbook mapping

    def subscribe_symbol(self, symbol: str):
        """Subscribe to market data for the symbol"""
        xt_market.subscribe_whole_quote([symbol], callback=self.on_market_update)

    def subscribe_all_markets(self):
        """Subscribe to market data for all markets (SH and SZ)"""
        xt_market.subscribe_whole_quote(['SH', 'SZ'], callback=self.on_market_update)
        logger.info("market data subscribed to SH and SZ")

    def on_market_update(self, data):
        """Callback to update orderbooks from market data"""
        # Assuming data contains kline or quote info
        for symbol, quote in data.items():
            if quote:
                # Get latest price from quote data
                last_price = quote.get('lastPrice')
                if last_price > 0:
                    # Create or update Orderbook
                    if symbol not in self.orderbooks:
                        self.orderbooks[symbol] = Orderbook(symbol)
                    orderbook = self.orderbooks[symbol]
                    orderbook.ask_px = quote.get('askPrice')
                    orderbook.bid_px = quote.get('bidPrice')
                    orderbook.ask_vol = quote.get('askVol')
                    orderbook.bid_vol = quote.get('bidVol')
                    # logger.info("Updated orderbook for %s with price %.2f", symbol, last_price)

    def get_orderbook(self, symbol: str) -> Optional[Orderbook]:
        """Get the orderbook for a symbol, subscribing if necessary"""
        if symbol not in self.orderbooks:
            self.subscribe_symbol(symbol)
            # Immediately try to get market data to populate orderbook
            data = xt_market.get_market_data_ex(symbol, period="1d", count=1)
            if data and symbol in data:
                self.on_market_update(data)
        return self.orderbooks.get(symbol)

    def run(self):
        """Start the market data loop"""
        xt_market.run()


market_manager = MarketManager()