from asset.use_cases.simulate import *
from datetime import datetime
from decimal import Decimal
from mpl_interactions import ioff, panhandler, zoom_factory
import plotly.express as px
from plotly.graph_objs import *


from_date = datetime.strptime("2009-01-01", "%Y-%m-%d").date()
end_date = datetime.strptime("2023-07-01", "%Y-%m-%d").date()
ticker = "SPY"


strategy_state = StrategyState(
    not_invested_amount=Decimal("1000"),
    number_of_assets=Decimal("0"),
    aggregate_amount=Decimal("200"),
)

strategy_configuration = StrategyConfiguration(
    bullish_attractive_percentage=Decimal("0.00"),
    bearish_attractive_percentage=Decimal("-0.06"),
    ema_period=Decimal("55"),
    number_of_registers_for_trend=90,
    number_of_registers_for_biggest_distance=30,
)


simulate = MopitzStrategySimulation(
    strategy_state=strategy_state, strategy_configuration=strategy_configuration
)


simulate.execute(ticker=ticker, from_date=from_date, end_date=end_date)
fig = px.line(simulate.final_data_frame, x="date", y="total_amount")

fig.update_layout(plot_bgcolor="white")
fig.update_xaxes(
    mirror=True,
    ticks="outside",
    showline=True,
    linecolor="black",
    gridcolor="lightgrey",
)
fig.update_yaxes(
    mirror=True,
    ticks="outside",
    showline=True,
    linecolor="black",
    gridcolor="lightgrey",
)

fig.show(config={"scrollZoom": True})
print(simulate.strategy_state.number_of_assets)


simulate.execute(ticker=ticker, from_date=from_date, end_date=end_date)
fig = px.line(simulate.final_data_frame, x="date", y="total_amount")

fig.update_layout(plot_bgcolor="white")
fig.update_xaxes(
    mirror=True,
    ticks="outside",
    showline=True,
    linecolor="black",
    gridcolor="lightgrey",
)
fig.update_yaxes(
    mirror=True,
    ticks="outside",
    showline=True,
    linecolor="black",
    gridcolor="lightgrey",
)

fig.show(config={"scrollZoom": True})
print(simulate.strategy_state.number_of_assets)


strategy_state = StrategyState(
    not_invested_amount=Decimal("1000"),
    number_of_assets=Decimal("0"),
    aggregate_amount=Decimal("200"),
)

strategy_configuration = StrategyConfiguration(
    bullish_attractive_percentage=Decimal("0.03"),
    bearish_attractive_percentage=Decimal("-0.06"),
    ema_period=Decimal("55"),
    number_of_registers_for_trend=90,
    number_of_registers_for_biggest_distance=30,
)


simulate = DCAStrategySimulation(
    strategy_state=strategy_state, strategy_configuration=strategy_configuration
)


simulate.execute(ticker=ticker, from_date=from_date, end_date=end_date)
fig = px.line(simulate.final_data_frame, x="date", y="total_amount")
fig.show(config={"scrollZoom": True})
print(simulate.strategy_state.number_of_assets)
