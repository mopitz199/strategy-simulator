import pytest
import pandas

from utils.utils.data_frame_tool import DataFameTool


class TestDataFrameToolAddEma:
    def test_add_ema(self):
        data = {"col1": [1, 2], "col2": [3, 4]}
        data_frame = pandas.DataFrame(data=data)

        tool = DataFameTool(data_frame=data_frame)
        tool.add_ema(ema_period=55, reference_column_name="col2", ema_column_name="ema")
        assert list(tool.data_frame.columns) == ["col1", "col2", "ema"]


class TestDataFrameToolAddTrend:
    @pytest.mark.parametrize(
        "data,result",
        [
            ([1, 5, 4, 1, 3], ["none", "none", "bullish", "bearish", "bearish"]),
            ([1, 5, 4, 1, 4], ["none", "none", "bullish", "bearish", "lateral"]),
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
