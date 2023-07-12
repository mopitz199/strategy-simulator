from django.http import JsonResponse

from asset.models import Asset
from datetime import datetime

def simulate(request):
    asset = Asset.objects.get(ticker="SPY")
    candles = asset.candle_set.filter(periodicity="daily").order_by("candle_datetime")

    data = []
    for candle in candles:
        data.append({
            "timestamp": datetime.timestamp(candle.candle_datetime),
            "date": candle.candle_datetime.date(),
            "open": candle.open_price,
            "close": candle.close_price,
            "low": candle.low_price,
            "high": candle.high_price,
        })
    return JsonResponse({"data": data})
