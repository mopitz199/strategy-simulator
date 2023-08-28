import pandas
import pytest

from unittest.mock import patch, Mock

from asset.use_cases.simulate import *


class TestProcessIndexFunctions:
    @pytest.mark.parametrize(
        "value, result",
        [
            (pandas.Timestamp("2023-01-01"), "2023-01-01"),
        ],
    )
    def test_process_timestamp_to_date_index(self, value, result):
        process_value = ProcessIndexFunctions.process_timestamp_to_date_index(value)
        assert process_value == result


class TestSimulate:
    def test_build_index(self):
        data = {
            "date": [pandas.Timestamp("2023-01-01"), pandas.Timestamp("2023-04-15")]
        }
        simulate = Simulate(None, None)
        simulate.base_data_frame = pandas.DataFrame(data=data)
        simulate.build_index(
            column_name="date",
            process_index_function=ProcessIndexFunctions.process_timestamp_to_date_index,
        )
        assert simulate.data_index == {"2023-01-01": 0, "2023-04-15": 1}

    @pytest.mark.parametrize(
        "row,result",
        [
            (
                {
                    "ema": Decimal("29"),
                    "high": Decimal("100"),
                    "low": Decimal("30"),
                    "open": Decimal("60"),
                },
                Decimal("30.16"),
            ),
            (
                {
                    "ema": Decimal("28"),
                    "high": Decimal("100"),
                    "low": Decimal("30"),
                    "open": Decimal("60"),
                },
                None,
            ),
            (
                {
                    "ema": Decimal("80"),
                    "high": Decimal("100"),
                    "low": Decimal("30"),
                    "open": Decimal("60"),
                },
                Decimal("60"),
            ),
            (
                {
                    "ema": Decimal("50"),
                    "high": Decimal("100"),
                    "low": Decimal("30"),
                    "open": Decimal("60"),
                },
                Decimal("52"),
            ),
        ],
    )
    def test_get_bullish_purchase_price(self, row, result):
        strategy_configuration = StrategyConfiguration(
            number_of_registers_for_trend=0,
            number_of_registers_for_biggest_distance=0,
            ema_period=0,
            bullish_attractive_percentage=Decimal("0.04"),
        )
        simulate = MopitzStrategySimulation(
            strategy_state=None, strategy_configuration=strategy_configuration
        )

        bulllish_purchase_price = simulate.get_bullish_purchase_price(row=row)
        assert bulllish_purchase_price == result

    @pytest.mark.parametrize(
        "row,result",
        [
            (
                {
                    "ema": Decimal("70"),
                    "high": Decimal("100"),
                    "low": Decimal("30"),
                    "open": Decimal("60"),
                },
                Decimal("60"),
            ),
            (
                {
                    "ema": Decimal("35"),
                    "high": Decimal("100"),
                    "low": Decimal("30"),
                    "open": Decimal("60"),
                },
                Decimal("32.55"),
            ),
            (
                {
                    "ema": Decimal("200"),
                    "high": Decimal("100"),
                    "low": Decimal("30"),
                    "open": Decimal("60"),
                },
                Decimal("60"),
            ),
            (
                {
                    "ema": Decimal("30"),
                    "high": Decimal("100"),
                    "low": Decimal("30"),
                    "open": Decimal("60"),
                },
                None,
            ),
        ],
    )
    def test_get_bearish_purchase_price(self, row, result):
        strategy_configuration = StrategyConfiguration(
            number_of_registers_for_trend=0,
            number_of_registers_for_biggest_distance=0,
            ema_period=0,
            bearish_attractive_percentage=Decimal("-0.07"),
        )
        simulate = MopitzStrategySimulation(
            strategy_state=None, strategy_configuration=strategy_configuration
        )

        bulllish_purchase_price = simulate.get_bearish_purchase_price(row=row)
        assert bulllish_purchase_price == result

    @pytest.mark.parametrize(
        "purchase_price,last_purchase_date,last_purchase_price,trend,date,ema,all_time_high,borrow_amount_left,result",
        [
            (
                Decimal("100"),
                "2023-01-01",
                Decimal("90"),
                "bullish",
                "2023-01-10",
                Decimal("0"),
                Decimal("0"),
                Decimal("0"),
                Decimal("0"),
            ),
            (
                Decimal("80"),
                "2023-01-01",
                Decimal("100"),
                "bullish",
                "2023-01-30",
                Decimal("1"),
                Decimal("1"),
                Decimal("500"),
                Decimal("6.25"),
            ),
            (
                Decimal("80"),
                "2023-01-01",
                Decimal("100"),
                "bullish",
                "2023-01-30",
                Decimal("1"),
                Decimal("1"),
                Decimal("1500"),
                Decimal("12.5"),
            ),
            (
                Decimal("80"),
                "2023-01-01",
                Decimal("100"),
                "bearish",
                "2023-01-30",
                Decimal("85"),
                Decimal("150"),
                Decimal("1500"),
                Decimal("18.75"),
            ),
            (
                Decimal("80"),
                "2023-01-01",
                Decimal("100"),
                "bearish",
                "2023-01-30",
                Decimal("81"),
                Decimal("150"),
                Decimal("1500"),
                Decimal("2.84"),
            ),
        ],
    )
    @patch("asset.use_cases.simulate.MopitzStrategySimulation.get_borrow_amount_left")
    def test_get_number_of_assets_to_buy(
        self,
        mock_get_borrow_amount_left,
        purchase_price,
        last_purchase_date,
        last_purchase_price,
        trend,
        date,
        ema,
        all_time_high,
        borrow_amount_left,
        result,
    ):
        mock_row_date = Mock()
        mock_to_pydatetime = Mock()
        mock_row_date.to_pydatetime.return_value = mock_to_pydatetime
        mock_to_pydatetime.date.return_value = datetime.strptime(date, "%Y-%m-%d")

        mock_get_borrow_amount_left.return_value = borrow_amount_left

        strategy_state = StrategyState(
            not_invested_amount=Decimal("10000"),
            number_of_assets=0,
            aggregate_amount=Decimal("200"),
        )
        simulate = MopitzStrategySimulation(
            strategy_state=strategy_state, strategy_configuration=None
        )
        number_of_assets_to_buy, _ = simulate.get_number_of_assets_to_buy(
            purchase_price=purchase_price,
            last_purchase_date=datetime.strptime(last_purchase_date, "%Y-%m-%d"),
            last_purchase_price=last_purchase_price,
            row={
                "trend": trend,
                "date": mock_row_date,
                "ema": ema,
                "all_time_high": all_time_high,
            },
        )
        assert number_of_assets_to_buy == result

    @pytest.mark.parametrize(
        "date,trend,purchase_price",
        [
            ("2023-01-02", "bullish", Decimal("120")),
            ("2023-01-01", "bullish", Decimal("120")),
            ("2023-01-02", "bullish", None),
            ("2023-01-01", "bullish", None),
            ("2023-01-02", "bearish", Decimal("120")),
            ("2023-01-01", "bearish", Decimal("120")),
            ("2023-01-02", "bearish", None),
            ("2023-01-01", "bearish", None),
        ],
    )
    @patch(
        "asset.use_cases.simulate.MopitzStrategySimulation.get_bearish_purchase_price"
    )
    @patch(
        "asset.use_cases.simulate.MopitzStrategySimulation.get_bullish_purchase_price"
    )
    def test_process_day(
        self,
        mock_get_bullish_purchase_price,
        mock_get_bearish_purchase_price,
        date,
        trend,
        purchase_price,
    ):
        mock_get_bullish_purchase_price.return_value = purchase_price
        mock_get_bearish_purchase_price.return_value = purchase_price

        strategy_state = StrategyState(
            aggregate_amount=Decimal("200"),
            number_of_assets=Decimal("0"),
        )

        simulate = MopitzStrategySimulation(
            strategy_state=strategy_state, strategy_configuration=None
        )
        simulate.data_frame = pandas.DataFrame(
            data={"date": [pandas.Timestamp(date)], "trend": [trend]}
        )
        simulate.data_index = {date: 0}

        date = datetime.strptime(date, "%Y-%m-%d").date()

        result_purchase_price = simulate.process_day(
            date=date, row=simulate.data_frame.iloc[0]
        )
        assert purchase_price == result_purchase_price
