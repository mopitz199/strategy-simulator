from decimal import Decimal

import pytest
import pandas

from utils.utils.data_frame_tool import DataFameTool


class TestDataFrameToolAddEma:
    def test_add_ema(self):
        data = {
            "col1": [Decimal("1"), Decimal("2")],
            "col2": [Decimal("3"), Decimal("4")],
        }
        data_frame = pandas.DataFrame(data=data)

        tool = DataFameTool(data_frame=data_frame)
        tool.add_ema(ema_period=55, reference_column_name="col2", ema_column_name="ema")
        assert list(tool.data_frame.columns) == ["col1", "col2", "ema"]


class TestDataFrameToolAddTrend:
    @pytest.mark.parametrize(
        "data,result",
        [
            (
                [Decimal("1"), Decimal("5"), Decimal("4"), Decimal("1"), Decimal("3")],
                ["none", "none", "bullish", "bearish", "bearish"],
            ),
            (
                [Decimal("1"), Decimal("5"), Decimal("4"), Decimal("1"), Decimal("4")],
                ["none", "none", "bullish", "bearish", "lateral"],
            ),
        ],
    )
    def test_add_trend(self, data, result):
        data = {"ema": data}
        data_frame = pandas.DataFrame(data=data)

        tool = DataFameTool(data_frame=data_frame)
        tool.add_trend(
            number_of_registers=2, ema_column_name="ema", trend_column_name="trend"
        )
        assert tool.data_frame["trend"].tolist() == result


class TestDataFrameToolAddAtractivePercentage:
    @pytest.mark.parametrize(
        "low_data,ema_data,result",
        [
            (
                [
                    Decimal("100"),
                    Decimal("140"),
                    Decimal("120"),
                    Decimal("170"),
                    Decimal("80"),
                ],
                [
                    Decimal("90"),
                    Decimal("110"),
                    Decimal("118"),
                    Decimal("130"),
                    Decimal("145"),
                ],
                [
                    "none",
                    Decimal("55.56"),
                    Decimal("9.09"),
                    Decimal("44.07"),
                    Decimal("-38.46"),
                ],
            ),
            (
                [
                    Decimal("100"),
                    Decimal("80"),
                    Decimal("90"),
                    Decimal("50"),
                    Decimal("65"),
                ],
                [
                    Decimal("105"),
                    Decimal("95"),
                    Decimal("92"),
                    Decimal("75"),
                    Decimal("70"),
                ],
                [
                    "none",
                    Decimal("-23.81"),
                    Decimal("-5.26"),
                    Decimal("-45.65"),
                    Decimal("-13.33"),
                ],
            ),
        ],
    )
    def test_add_atractive_percentage(self, low_data, ema_data, result):
        data = {"low": low_data, "ema": ema_data}
        data_frame = pandas.DataFrame(data=data)
        tool = DataFameTool(data_frame=data_frame)
        tool.add_atractive_percentage(
            low_column_name="low",
            ema_column_name="ema",
            attractive_percentage_column_name="attractive_percentage",
        )
        assert tool.data_frame["attractive_percentage"].tolist() == result
