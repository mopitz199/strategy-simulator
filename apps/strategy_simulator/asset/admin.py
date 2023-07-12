from django.contrib import admin
from asset.models import Asset, Candle


class AssetAdmin(admin.ModelAdmin):
    pass

class CandleAdmin(admin.ModelAdmin):
    pass


admin.site.register(Asset, AssetAdmin)
admin.site.register(Candle, CandleAdmin)