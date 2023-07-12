from datetime import datetime

import pandas

from asset.repositories.asset import AssetRepository
from asset.repositories.candle import CandleRepository

class Simulate:

    def build_pandas_data_frame(self, candles):
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
    
    def add_ema(self, data_frame: pandas.DataFrame, ema_period: int):
        data_frame.sort_values(by='date', inplace = True, ascending = True)
        data_frame['ema'] = data_frame['close'].ewm(span=ema_period, adjust=False).mean()

    

    def execute(self, ticker: str, ema_period: int, from_date: datetime, end_date: datetime):
        asset = AssetRepository.get_asset({"ticker": ticker})
        candles = CandleRepository.get_candles({
            "asset_id": asset.id,
            "candle_datetime__range": [from_date, end_date],
            "periodicity": "daily"
        })
        data_frame = self.build_pandas_data_frame(candles=candles)
        self.add_ema(data_frame=data_frame, ema_period=ema_period)
        