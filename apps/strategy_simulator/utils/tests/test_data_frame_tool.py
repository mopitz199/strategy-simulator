import pandas

from utils.utils.data_frame_tool import DataFameTool


class TestDataFrameToolAddEma:
    def test_add_ema(self):
        d = {"col1": [1, 2], "col2": [3, 4]}
        data_frame = pandas.DataFrame(data=d)

        tool = DataFameTool(data_frame=data_frame)
        tool.add_ema(ema_period=55, reference_column_name="col2", ema_column_name="ema")
        assert list(tool.data_frame.columns) == ["col1", "col2", "ema"]
