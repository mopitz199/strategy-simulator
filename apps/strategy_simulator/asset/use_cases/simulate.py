from decimal import Decimal
from typing import Callable, Optional
from datetime import datetime, timedelta

import pandas

from django.db.models import QuerySet

from asset.repositories.asset import AssetRepository
from asset.repositories.candle import CandleRepository

from asset.use_cases.build_data_frame import BuildDataFrame
from utils.utils.data_frame_tool import DataFameTool


class ProcessIndexFunctions:
    @staticmethod
    def process_timestamp_to_date_index(value: pandas.Timestamp) -> str:
        return str(value.to_pydatetime().date())


class Simulate:
    def __init__(self, strategy_state):
        self.strategy_state = strategy_state
        self.data_frame = None
        self.data_index = None

    def build_index(self, column_name: str, process_index_function: Callable) -> dict:
        data_index = {}
        for index in self.data_frame.index:
            value = self.data_frame.iloc[index][column_name]
            processed_value = process_index_function(value)
            data_index[processed_value] = index
        self.data_index = data_index

    def build_complete_data_frame(self, candles: QuerySet) -> pandas.DataFrame:
        data_frame = BuildDataFrame.execute(candles=candles)
        data_frame_tool = DataFameTool(data_frame=data_frame)
        data_frame_tool.add_ema(
            ema_column_name="ema", ema_period=55, reference_column_name="close"
        )
        data_frame_tool.add_trend(
            number_of_registers=90, ema_column_name="ema", trend_column_name="trend"
        )
        data_frame_tool.add_atractive_percentage(
            low_column_name="low",
            ema_column_name="ema",
            attractive_percentage_column_name="attractive_percentage",
        )
        data_frame_tool.add_biggest_distances(
            number_of_registers=30,
            low_column_name="low",
            high_column_name="high",
            biggest_high_column_name="biggest_high",
            lowest_low_column_name="lowest_low",
        )
        return data_frame_tool.data_frame

    def get_bullish_purchase_price(self, row) -> Optional[Decimal]:
        aux_buyer_price = row["ema"] * (
            1 + self.strategy_state["bullish_attractive_percentage"]
        )

        if row["low"] <= aux_buyer_price <= row["high"]:
            if row["open"] <= aux_buyer_price:
                final_buyer_price = row["open"]
            else:
                final_buyer_price = aux_buyer_price
        elif row["high"] < aux_buyer_price:
            final_buyer_price = row["open"]
        else:
            final_buyer_price = None
        return final_buyer_price

    def get_bearish_purchase_price(self, row) -> Optional[Decimal]:
        aux_buyer_price = row["ema"] * (
            1 + self.strategy_state["bearish_attractive_percentage"]
        )

        if row["low"] <= aux_buyer_price <= row["high"]:
            if row["open"] <= aux_buyer_price:
                final_buyer_price = row["open"]
            else:
                final_buyer_price = aux_buyer_price
        elif row["high"] < aux_buyer_price:
            final_buyer_price = row["open"]
        else:
            final_buyer_price = None
        return final_buyer_price

    def get_number_of_assets_to_buy(self, purchase_price: Decimal):
        return round(self.strategy_state["not_invested_amount"] / purchase_price, 2)

    def process_day(self, date: datetime.date):
        if date.weekday() == 6:
            self.strategy_state["not_invested_amount"] += self.strategy_state[
                "aggregate_amount"
            ]

        index_row = self.data_index.get(str(date))
        if index_row is not None:
            row = self.data_frame.iloc[index_row]
            if row["trend"] == "bullish":
                purchase_price = self.get_bullish_purchase_price(row=row)
            elif row["trend"] == "bearish":
                purchase_price = self.get_bearish_purchase_price(row=row)

        if purchase_price is not None:
            number_of_assets = self.get_number_of_assets_to_buy(
                purchase_price=purchase_price
            )
            self.strategy_state["number_of_assets"] = number_of_assets
            self.strategy_state["not_invested_amount"] = Decimal("0")

    def execute(self, ticker: str, from_date: datetime, end_date: datetime):
        asset = AssetRepository.get_asset({"ticker": ticker})
        candles = CandleRepository.get_candles(
            {
                "asset_id": asset.id,
                "candle_datetime__range": [from_date, end_date],
                "periodicity": "daily",
            }
        )
        self.data_frame = self.build_complete_data_frame(candles=candles)
        self.build_index(
            column_name="date",
            process_index_function=ProcessIndexFunctions.process_timestamp_to_date_index,
        )

        aux_date = from_date
        while aux_date <= end_date:
            self.process_day(date=aux_date)
            aux_date += timedelta(days=1)
