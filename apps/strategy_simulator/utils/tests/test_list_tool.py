from decimal import Decimal

import pytest

from utils.utils.list_tool import ListTool


class TestListTool:
    @pytest.mark.parametrize(
        "start_index,end_index,max_result",
        [
            (0, 10, (Decimal("20"), 6)),
            (6, 8, (Decimal("20"), 6)),
            (1, 5, (Decimal("19"), 1)),
        ],
    )
    def test_get_max_from_list(
        self,
        start_index,
        end_index,
        max_result,
    ):
        values_list = [
            Decimal("1"),
            Decimal("19"),
            Decimal("2"),
            Decimal("9"),
            Decimal("18"),
            Decimal("8"),
            Decimal("20"),
            Decimal("12"),
            Decimal("15"),
            Decimal("6"),
            Decimal("16"),
        ]
        assert (
            ListTool.get_max_from_list(
                values_list=values_list, start_index=start_index, end_index=end_index
            )
            == max_result
        )

    @pytest.mark.parametrize(
        "start_index,end_index,min_result",
        [
            (0, 10, (Decimal("-2"), 2)),
            (6, 8, (Decimal("12"), 7)),
            (1, 6, (Decimal("-2"), 2)),
            (6, 10, (Decimal("6"), 9)),
        ],
    )
    def test_get_min_from_list(
        self,
        start_index,
        end_index,
        min_result,
    ):
        values_list = [
            Decimal("1"),
            Decimal("19"),
            Decimal("-2"),
            Decimal("9"),
            Decimal("18"),
            Decimal("8"),
            Decimal("20"),
            Decimal("12"),
            Decimal("15"),
            Decimal("6"),
            Decimal("16"),
        ]
        assert (
            ListTool.get_min_from_list(
                values_list=values_list, start_index=start_index, end_index=end_index
            )
            == min_result
        )
