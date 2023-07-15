from typing import Tuple


class ListTool:
    @staticmethod
    def get_max_from_list(
        values_list: list,
        start_index: int = 0,
        end_index: int = 0,
    ) -> Tuple:
        max_value, max_value_index = None, None

        for index in range(start_index, end_index + 1):
            value = values_list[index]
            if max_value is None:
                max_value = value
                max_value_index = index
            else:
                if max_value < value:
                    max_value = value
                    max_value_index = index
        return max_value, max_value_index

    @staticmethod
    def get_min_from_list(
        values_list: list,
        start_index: int = 0,
        end_index: int = 0,
    ) -> Tuple:
        min_value, min_value_index = None, None

        for index in range(start_index, end_index + 1):
            value = values_list[index]
            if min_value is None:
                min_value = value
                min_value_index = index
            else:
                if min_value > value:
                    min_value = value
                    min_value_index = index
        return min_value, min_value_index
