from asset.models import Candle

class CandleRepository:

    @staticmethod
    def get_candle(**filters):
        return Candle.objects.get(**filters)
    
    @staticmethod
    def get_candles(**filters):
        return Candle.objects.filter(**filters)
