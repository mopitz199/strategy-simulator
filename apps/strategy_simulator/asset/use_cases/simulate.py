from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Optional
from datetime import datetime, timedelta

import pandas

from django.db.models import QuerySet

from asset.repositories.asset import AssetRepository
from asset.repositories.candle import CandleRepository

from asset.use_cases.build_data_frame import BuildDataFrame
from utils.utils.data_frame_tool import DataFameTool


@dataclass
class StrategyState:
    not_invested_amount: Optional[Decimal] = None
    aggregate_amount: Optional[Decimal] = None
    number_of_assets: Optional[Decimal] = None


@dataclass
class StrategyConfiguration:
    number_of_registers_for_trend: int
    number_of_registers_for_biggest_distance: int
    ema_period: Decimal
    bearish_attractive_percentage: Optional[Decimal] = None
    bullish_attractive_percentage: Optional[Decimal] = None


@dataclass
class StrategyHistoryExecution:
    buy_prices: dict[list[Decimal]]
    buy_prices_date: dict[list[str]]
    amount_invested: dict[list[Decimal]]

    def __init__(self):
        self.buy_prices = {}
        self.buy_prices_date = {}
        self.amount_invested = {}

    def add_buy_price(self, color, value):
        if color not in self.buy_prices:
            self.buy_prices[color] = []
        self.buy_prices[color].append(value)

    def add_buy_prices_date(self, color, value):
        if color not in self.buy_prices_date:
            self.buy_prices_date[color] = []
        self.buy_prices_date[color].append(value)

    def add_amount_invested(self, color, value):
        if color not in self.amount_invested:
            self.amount_invested[color] = []
        self.amount_invested[color].append(value)


class ProcessIndexFunctions:
    @staticmethod
    def process_timestamp_to_date_index(value: pandas.Timestamp) -> str:
        return str(value.to_pydatetime().date())


class Simulate:
    def __init__(
        self,
        strategy_state: StrategyState,
        strategy_configuration: StrategyConfiguration,
    ):
        self.strategy_state = (
            strategy_state  # All the info ro configure the strategy paraemters
        )
        self.strategy_configuration = (
            strategy_configuration  # All the info ro configure the strategy paraemters
        )
        self.history_execution = StrategyHistoryExecution()

        self.base_data_frame = (
            None  # The main data frame with the info of the whole asset history
        )
        self.data_index = (
            {}
        )  # Index to get a row of the base_data_frame from any key(eg: date)

    def build_index(self, column_name: str, process_index_function: Callable) -> dict:
        data_index = {}
        for index in self.base_data_frame.index:
            value = self.base_data_frame.iloc[index][column_name]
            processed_value = process_index_function(value)
            data_index[processed_value] = index
        self.data_index = data_index

    def get_row(self, date: datetime.date):
        index_row = self.data_index.get(str(date))
        row = None
        if index_row:
            row = self.base_data_frame.iloc[index_row]
        return row

    def build_complete_data_frame(self, candles: QuerySet) -> pandas.DataFrame:
        data_frame = BuildDataFrame.execute(candles=candles)
        data_frame_tool = DataFameTool(data_frame=data_frame)
        data_frame_tool.add_ema(
            ema_column_name="ema",
            ema_period=self.strategy_configuration.ema_period,
            reference_column_name="close",
        )
        data_frame_tool.add_trend(
            number_of_registers=self.strategy_configuration.number_of_registers_for_trend,
            ema_column_name="ema",
            trend_column_name="trend",
        )
        data_frame_tool.add_atractive_percentage(
            low_column_name="low",
            ema_column_name="ema",
            attractive_percentage_column_name="attractive_percentage",
        )
        data_frame_tool.add_biggest_distances(
            number_of_registers=self.strategy_configuration.number_of_registers_for_biggest_distance,
            low_column_name="low",
            high_column_name="high",
            biggest_high_column_name="biggest_high",
            lowest_low_column_name="lowest_low",
        )
        data_frame_tool.add_all_time_high_and_low(
            low_column_name="low",
            high_column_name="high",
            all_time_high_column_name="all_time_high",
            all_time_low_column_name="all_time_low",
        )
        return data_frame_tool.data_frame

    def get_number_of_assets_to_buy(
        self,
        purchase_price: Decimal,
        last_purchase_date: Optional[datetime],
        last_purchase_price: Optional[Decimal],
        row=None,
    ):
        return (
            round(self.strategy_state.not_invested_amount / purchase_price, 2),
            "green",
        )

    def fill_aggregate_amount(self):
        self.strategy_state.not_invested_amount += self.strategy_state.aggregate_amount

    def should_we_aggregate_amount(self, date: datetime.date):
        return date.weekday() == 6

    def get_total_amount(self, price: Decimal = None):
        return self.strategy_state.not_invested_amount + (
            self.strategy_state.number_of_assets * price
        )

    def execute(self, ticker: str, from_date: datetime, end_date: datetime):
        asset = AssetRepository.get_asset({"ticker": ticker})
        candles = CandleRepository.get_candles(
            {
                "asset_id": asset.id,
                "candle_datetime__lte": end_date,
                "periodicity": "daily",
            },
            order_by="candle_datetime",
        )
        self.base_data_frame = self.build_complete_data_frame(candles=candles)
        self.build_index(
            column_name="date",
            process_index_function=ProcessIndexFunctions.process_timestamp_to_date_index,
        )

        self.total_amount = []
        self.total_not_invested_amount = []

        first_index = None

        last_purchase_date = None
        last_purchase_price = None

        aux_date = from_date
        while aux_date <= end_date:
            if self.should_we_aggregate_amount(date=aux_date):
                self.fill_aggregate_amount()

            row = self.get_row(aux_date)

            if row is not None:
                if first_index is None:
                    first_index = self.data_index.get(str(aux_date))

                purchase_price = self.process_day(date=aux_date, row=row)

                if purchase_price:
                    number_of_assets, color = self.get_number_of_assets_to_buy(
                        purchase_price=purchase_price,
                        last_purchase_date=last_purchase_date,
                        last_purchase_price=last_purchase_price,
                        row=row,
                    )
                    amount_to_invest = number_of_assets * purchase_price

                    self.strategy_state.number_of_assets += number_of_assets
                    self.strategy_state.not_invested_amount -= amount_to_invest

                    if amount_to_invest:
                        last_purchase_date = aux_date
                        last_purchase_price = purchase_price

                        self.history_execution.add_buy_price(
                            color=color, value=purchase_price
                        )
                        self.history_execution.add_buy_prices_date(
                            color=color, value=str(aux_date)
                        )
                        self.history_execution.add_amount_invested(
                            color=color, value=amount_to_invest
                        )

                if first_index is not None:
                    self.total_amount.append(self.get_total_amount(price=row["close"]))
                    self.total_not_invested_amount.append(
                        self.strategy_state.not_invested_amount
                    )

            aux_date += timedelta(days=1)

        self.final_data_frame = self.base_data_frame.iloc[first_index:]
        self.final_data_frame["total_amount"] = self.total_amount
        self.final_data_frame["not_invested_amount"] = self.total_not_invested_amount


class MopitzStrategySimulation(Simulate):
    def get_percentage_between_ema_and_purchase_price(
        self, purchase_price: Decimal, ema: Decimal
    ) -> Decimal:
        percentage = (purchase_price * 100) / ema - 100
        percentage = round(percentage, 2)
        return percentage

    def get_borrow_amount_left(self):
        return self.strategy_state.aggregate_amount * 54 + min(
            self.strategy_state.not_invested_amount, Decimal("0")
        )

    def get_color(self, amount_to_invest):
        if Decimal("0") < amount_to_invest <= Decimal("200"):
            return "#37d43c"
        elif Decimal("200") < amount_to_invest <= Decimal("500"):
            return "#eb6805"
        elif Decimal("500") < amount_to_invest <= Decimal("1000"):
            return "#f70000"
        elif Decimal("1000") < amount_to_invest <= Decimal("3000"):
            return "#f700df"
        elif Decimal("3000") < amount_to_invest <= Decimal("10000"):
            return "#960000"
        elif Decimal("10000") < amount_to_invest:
            return "#960082"
        else:
            return "#1c1a1a"

    def get_number_of_assets_to_buy(
        self,
        purchase_price: Decimal,
        last_purchase_date: Optional[datetime],
        last_purchase_price: Optional[Decimal],
        row=None,
    ):
        row_date = row["date"].to_pydatetime().date()
        if (
            last_purchase_price
            and purchase_price is not None
            and 100 - ((last_purchase_price * 100) / purchase_price) > -5
            and last_purchase_date + timedelta(days=21) > row_date
        ):
            return Decimal("0"), "black"

        amount_to_invest = Decimal("0")

        percentage = self.get_percentage_between_ema_and_purchase_price(
            purchase_price=purchase_price, ema=row["ema"]
        )
        absolute_percentage = abs(percentage)
        borrow_amount_left = self.get_borrow_amount_left()

        if row["trend"] == "bullish":
            week_factor = Decimal("5")
            amount_to_invest = min(
                self.strategy_state.aggregate_amount * week_factor, borrow_amount_left
            )
        elif row["trend"] == "bearish":
            aux_amount_to_invest = (
                row["all_time_high"] * absolute_percentage * absolute_percentage
            )
            amount_to_invest = min(aux_amount_to_invest, borrow_amount_left)

        number_of_assets = amount_to_invest / purchase_price
        return round(number_of_assets, 2), self.get_color(
            amount_to_invest=amount_to_invest
        )

    def get_bullish_purchase_price(self, row) -> Optional[Decimal]:
        aux_buyer_price = row["ema"] * (
            1 + self.strategy_configuration.bullish_attractive_percentage
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
            1 + self.strategy_configuration.bearish_attractive_percentage
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

    def process_day(self, date: datetime.date, row):
        purchase_price = None

        if row["trend"] == "bullish":
            purchase_price = self.get_bullish_purchase_price(row=row)
        elif row["trend"] == "bearish":
            purchase_price = self.get_bearish_purchase_price(row=row)

        return purchase_price


class DCAStrategySimulation(Simulate):
    def process_day(self, date: datetime.date, row):
        index_row = self.data_index.get(str(date))
        purchase_price = None

        if index_row % 7 == 0:
            purchase_price = row["open"]

        return purchase_price
