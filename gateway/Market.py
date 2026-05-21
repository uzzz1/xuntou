import logging
from typing import Any, Callable, List, Optional, Union

from xtquant import xtdata
from model.model import singleton

logger = logging.getLogger(__name__)

MarketCode = Union[str, List[str]]
MarketCallback = Callable[[Any], None]


def _ensure_list(code_list: MarketCode) -> List[str]:
    if isinstance(code_list, str):
        return [code_list]
    return list(code_list)


@singleton
class XtMarket:
    def __init__(self):
        self._subscribed_codes = set()

    def download_history_data(self, code_list: MarketCode, period: str = "1d", incrementally: bool = True) -> None:
        codes = _ensure_list(code_list)
        for code in codes:
            xtdata.download_history_data(code, period=period, incrementally=incrementally)
            logger.info("download_history_data success code=%s period=%s incrementally=%s", code, period, incrementally)

    def download_financial_data(self, code_list: MarketCode) -> Any:
        codes = _ensure_list(code_list)
        result = xtdata.download_financial_data(codes)
        logger.info("download_financial_data success codes=%s", codes)
        return result

    def download_sector_data(self) -> Any:
        result = xtdata.download_sector_data()
        logger.info("download_sector_data success")
        return result

    def get_market_data_ex(self, code_list: MarketCode, period: str = "1d", count: int = -1) -> Any:
        codes = _ensure_list(code_list)
        result = xtdata.get_market_data_ex([], codes, period=period, count=count)
        logger.info("get_market_data_ex codes=%s period=%s count=%s", codes, period, count)
        return result

    def subscribe_whole_quote(self, code_list: List[str], callback: Optional[MarketCallback] = None) -> Any:
        ret = xtdata.subscribe_whole_quote(code_list, callback=callback)
        if ret > 0:
            for code in code_list:
                self._subscribed_codes.add(code)
            logger.info("subscribe_whole_quote success codes=%s", code_list)
        else:
            logger.error("subscribe_whole_quote failed codes=%s ret=%s", code_list, ret)
        return ret

    def unsubscribe_quote(self, code: str, period: str = "1d") -> Any:
        if hasattr(xtdata, "unsubscribe_quote"):
            ret = xtdata.unsubscribe_quote(code, period=period)
            if ret == 0 or ret is True:
                self._subscribed_codes.discard(code)
                logger.info("unsubscribe_quote success code=%s period=%s", code, period)
            else:
                logger.error("unsubscribe_quote failed code=%s period=%s ret=%s", code, period, ret)
            return ret
        logger.warning("unsubscribe_quote not supported by xtdata")
        return None

    def run(self) -> None:
        logger.info("XtMarket run start")
        xtdata.run()


xt_market = XtMarket()


# if __name__ == "__main__":
#     market = XtMarket()
#     code_list = ["000001.SZ"]
#     period = "1d"

#     for code in code_list:
#         market.download_history_data(code, period=period, incrementally=True)

#     market.download_financial_data(code_list)
#     market.download_sector_data()

#     history_data = market.get_market_data_ex(code_list, period=period, count=-1)
#     print(history_data)
#     print("=" * 20)

#     for code in code_list:
#         market.subscribe_quote(code, period=period, count=-1)

#     import time
#     time.sleep(1)

#     kline_data = market.get_market_data_ex(code_list, period=period)
#     print(kline_data)

#     for i in range(10):
#         kline_data = market.get_market_data_ex(code_list, period=period)
#         print(kline_data)
#         time.sleep(3)

#     def on_market_update(data: Any) -> None:
#         codes = list(data.keys())
#         kline_in_callback = market.get_market_data_ex(codes, period=period)
#         print(kline_in_callback)

#     for code in code_list:
#         market.subscribe_quote(code, period=period, count=-1, callback=on_market_update)

#     market.run()
