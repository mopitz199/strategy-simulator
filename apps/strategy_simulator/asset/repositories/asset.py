from asset.models import Asset


class AssetRepository:
    @staticmethod
    def get_asset(filters):
        return Asset.objects.get(**filters)

    @staticmethod
    def get_assets(filters):
        return Asset.objects.filter(**filters)
