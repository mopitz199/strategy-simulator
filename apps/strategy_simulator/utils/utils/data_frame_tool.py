from utils import constants as utils_constants

class DataFameTool:

    def __init__(self, data_frame):
        self.data_frame = data_frame

    def add_ema(
            self,
            ema_period: int,
            reference_column_name: str,
            ema_column_name: str,
        ):
        self.data_frame[ema_column_name] = self.data_frame[reference_column_name].ewm(
            span=ema_period, adjust=False
        ).mean()

    def add_trend(self, number_of_registers, ema_column_name: str, trend_column_name: str):
        if ema_column_name not in list(self.data_frame.columns):
            raise Exception("Ema column does not exists")
        else:
            trends = ["None"]*number_of_registers
            ema_values = self.data_frame[ema_column_name].tolist()

            for index in range(number_of_registers, len(ema_values)-1):
                start_ema_value = ema_values[index-number_of_registers]
                end_ema_value = ema_values[index]

                if start_ema_value > end_ema_value:
                    trend = utils_constants.BEARISH_TREND
                elif start_ema_value < end_ema_value:
                    trend = utils_constants.BULLISH_TREND
                else:
                    trend = utils_constants.LATERAL_TREND
                trends.append(trend)

            self.data_frame[trend_column_name] = trends   