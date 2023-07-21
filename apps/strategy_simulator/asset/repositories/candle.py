from asset.models import Candle


class CandleRepository:
    @staticmethod
    def get_candle(filters):
        return Candle.objects.get(**filters)

    @staticmethod
    def get_candles(filters, order_by: str = None):
        if order_by:
            return Candle.objects.filter(**filters).order_by(order_by)
        else:
            return Candle.objects.filter(**filters)
