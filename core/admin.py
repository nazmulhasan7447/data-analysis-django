from django.contrib import admin
from .models import PackageItems, PackageName, PackagePurchaseHistory, Message

admin.site.register(PackageName)
admin.site.register(PackageItems)
admin.site.register(PackagePurchaseHistory)

admin.site.register(Message)