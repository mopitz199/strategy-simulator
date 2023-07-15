import pandas
import pytest

from model_bakery import baker

from asset.models import Asset, Candle
from asset.use_cases.build_data_frame import BuildDataFrame


class TestBuildDataFame:
    @pytest.mark.django_db
    def test_build_data_frame(self):
        asset = baker.make(Asset)

        candles = []
        for i in range(0, 2):
            candles.append(baker.make(Candle, asset=asset))

        data_frame = BuildDataFrame.execute(candles=candles)
        data_frame["date"] = pandas.to_datetime(data_frame["date"])

        row_1 = data_frame.iloc[0].tolist()
        row_1[0] = row_1[0].to_pydatetime()

        row_2 = data_frame.iloc[1].tolist()
        row_2[0] = row_2[0].to_pydatetime()

        assert row_1 == [
            candles[0].candle_datetime,
            candles[0].open_price,
            candles[0].close_price,
            candles[0].high_price,
            candles[0].low_price,
        ]
