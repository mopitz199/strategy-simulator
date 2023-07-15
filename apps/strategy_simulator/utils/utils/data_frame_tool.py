from utils import constants as utils_constants
from utils.utils.list_tool import ListTool


class DataFameTool:
    def __init__(self, data_frame):
        self.data_frame = data_frame

    """It gives us the Exponensial Moving Average"""

    def add_ema(
        self,
        ema_period: int,
        reference_column_name: str,
        ema_column_name: str,
    ):
        self.data_frame[ema_column_name] = (
            self.data_frame[reference_column_name]
            .ewm(span=ema_period, adjust=False)
            .mean()
        )

    """The trend basically indicate us if the tendency of the last X
    registers has been bullish, bearish or lateral until the current day"""

    def add_trend(
        self,
        number_of_registers,
        ema_column_name: str,
        trend_column_name: str,
    ):
        if ema_column_name not in list(self.data_frame.columns):
            raise Exception("EMA column should be added first")

        trends = [utils_constants.NONE_CONSTANT] * number_of_registers
        ema_values = self.data_frame[ema_column_name].tolist()

        for index in range(number_of_registers, len(ema_values)):
            start_ema_value = ema_values[index - number_of_registers]
            end_ema_value = ema_values[index]

            if start_ema_value > end_ema_value:
                trend = utils_constants.BEARISH_TREND
            elif start_ema_value < end_ema_value:
                trend = utils_constants.BULLISH_TREND
            else:
                trend = utils_constants.LATERAL_TREND
            trends.append(trend)
        self.data_frame[trend_column_name] = trends

    """The attractive perecentage is the difference bewteen the lowest
    price of the day and the ema of the day before. It allow us to
    determine the opportunities of the current day"""

    def add_atractive_percentage(
        self,
        low_column_name: str,
        ema_column_name: str,
        attractive_percentage_column_name: str,
    ):
        if ema_column_name not in list(self.data_frame.columns):
            raise Exception("EMA column should be added first")
        if low_column_name not in list(self.data_frame.columns):
            raise Exception("Low column should be added first")

        ema_values = self.data_frame[ema_column_name].tolist()
        low_prices = self.data_frame[low_column_name].tolist()

        percentage_difference_column = [utils_constants.NONE_CONSTANT]

        for index in range(1, len(ema_values)):
            low_price = low_prices[index]
            ema_value = ema_values[index - 1]
            percentage = (low_price * 100) / ema_value - 100
            percentage = round(percentage, 2)
            percentage_difference_column.append(percentage)

        self.data_frame[
            attractive_percentage_column_name
        ] = percentage_difference_column

    """The biggest distance is the minimum or maximum value starting from the current
    day backing into the last X registers"""

    def add_biggest_distances(
        self,
        number_of_registers: int,
        low_column_name: str,
        high_column_name: str,
        biggest_high_column_name: str,
        lowest_low_column_name: str,
    ):
        low_prices = self.data_frame[low_column_name].tolist()
        high_prices = self.data_frame[high_column_name].tolist()
        start_index = 0

        max_price, max_price_index = ListTool.get_max_from_list(
            values_list=high_prices,
            start_index=start_index,
            end_index=number_of_registers - 1,
        )
        min_price, min_price_index = ListTool.get_min_from_list(
            values_list=low_prices,
            start_index=start_index,
            end_index=number_of_registers - 1,
        )

        max_prices_columns = [utils_constants.NONE_CONSTANT] * number_of_registers
        min_prices_columns = [utils_constants.NONE_CONSTANT] * number_of_registers
        for index in range(number_of_registers, len(low_prices)):
            max_prices_columns.append(max_price)
            min_prices_columns.append(min_price)

            start_index = index - (number_of_registers - 1)

            if max_price < high_prices[index]:
                max_price, max_price_index = high_prices[index], index
            else:
                if start_index > max_price_index:
                    max_price, max_price_index = ListTool.get_max_from_list(
                        values_list=high_prices,
                        start_index=start_index,
                        end_index=index,
                    )

            if min_price > low_prices[index]:
                min_price, min_price_index = low_prices[index], index
            else:
                if start_index > min_price_index:
                    min_price, min_price_index = ListTool.get_min_from_list(
                        values_list=low_prices,
                        start_index=start_index,
                        end_index=index,
                    )

        self.data_frame[biggest_high_column_name] = max_prices_columns
        self.data_frame[lowest_low_column_name] = min_prices_columns
