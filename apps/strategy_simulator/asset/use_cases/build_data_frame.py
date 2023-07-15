from typing import List

import pandas

from asset.models import Candle


class BuildDataFrame:
    @staticmethod
    def execute(candles: List[Candle]):
        data = {
            "date": [],
            "open": [],
            "close": [],
            "high": [],
            "low": [],
        }

        for candle in candles:
            data["date"].append(candle.candle_datetime)
            data["open"].append(candle.open_price)
            data["close"].append(candle.close_price)
            data["high"].append(candle.high_price)
            data["low"].append(candle.low_price)

        data_frame = pandas.DataFrame(data=data)
        return data_frame
