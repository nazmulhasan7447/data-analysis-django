from django.contrib import admin
from django.urls import path, re_path, include
from .views import *

urlpatterns = [
    re_path(r'^check/symbool/$', IsSymboolOkay.as_view(), name='checkSymbool'),
    re_path(r'^get/perpetualgrowth/cost_of/equity/$', GetPerpetualGrowthCostOfEquity.as_view(), name='getPerpetualGrowthCostofEquity'),
    re_path(r'^get/perpetualgrowth/cost_of/debt/$', GetPerpetualCostOfDebt.as_view(), name='getPerpetualGrowthCostofDebt'),
    re_path(r'^get/perpetualgrowth/rate/(?P<userID>[-\w]+)/$', GetPerpetualGrowthRateView.as_view(), name='getGetPerpetualGrowthRateView'),
    re_path(r'^get/perpetual/growth/history/$', GetPerpetualGrowthRateHistoryView.as_view(), name="getPerpetualGrowthHistory"),

    re_path(r'^user-list/$', AllUsersAccountView.as_view(), name='userList'),
    re_path(r'^user-details/(?P<user_id>\w+)/$', AccountDetailsView.as_view(), name='userDetails'),
    re_path(r'^create-account/$', CreateAccountView.as_view(), name='createAccount'),
    re_path(r'^package-item-list/$', PackageItemListView.as_view(), name='pakageItemList'),
    re_path(r'^package-list/$', PackageListView.as_view(), name='pakageList'),
    re_path(r'^package-details/(?P<package_id>\w+)/$', PackageDetailsView.as_view(), name='packageDetails'),
    re_path(r'^package-purchase-history/$', PackagePurchaseHistoryView.as_view(), name='packagePurchaseHistoryView'),
    re_path(r'^create-payment-intent/$', PaymentView.as_view(), name='paymentView'),

    # message
    re_path(r'^user/messages/$', MessageView.as_view(), name='userMessages'),

    re_path(r'^user/change/password/(?P<user_id>\w+)/$', ChangePasswordView.as_view(), name='userChangePassword'),
    re_path(r'^user/forgot/password/$', ForgotPassword.as_view(), name='forgotPassword'),
    re_path(r'^upload/profile/image/$', UploadProfileImageView.as_view(), name='uploadProfileImage'),
    re_path(r'^unsubscribe/(?P<username>\w+)/$', Unsubscribe.as_view(), name='unsubscribe'),
    re_path(r'^free/trail/(?P<userID>\w+)/$', StartFreeTrialView.as_view(), name='startSevenDaysFreeTrial'),
]
