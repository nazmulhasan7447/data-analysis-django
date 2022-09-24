from django.contrib import admin
from .models import PackageItems, PackageName, PackagePurchaseHistory, Message, PerpetualGrowthRateData, EstimatedIntrinsicValueData, NumberOfRequestByUser

admin.site.register(PackageName)
admin.site.register(PackageItems)
admin.site.register(PackagePurchaseHistory)

admin.site.register(Message)
admin.site.register(PerpetualGrowthRateData)

admin.site.register(EstimatedIntrinsicValueData)

admin.site.register(NumberOfRequestByUser)