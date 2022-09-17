from django.db import models
from user.models import Account
from django.utils.crypto import get_random_string


class PackageItems(models.Model):
    item_description = models.CharField(max_length=255)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item_description


class PackageName(models.Model):

    willCharge = (
        ('month', 'Per Month'),
        ('year', 'Per Year'),
    )

    packageType = (
        ('free', 'Free Membership'),
        ('pro_paid', 'Pro Membership')
    )
    package_id = models.CharField(max_length=20, blank=True, null=True)
    package_type = models.CharField(max_length=255, choices=packageType, blank=True, null=True)
    name = models.CharField(max_length=100)
    sub_title = models.CharField(max_length=255)
    price = models.FloatField(default=0)
    willBeCharged = models.CharField(max_length=50, choices=willCharge)
    items = models.ManyToManyField(PackageItems, related_name="package_items")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.package_id = get_random_string(20)
        super(PackageName, self).save(*args, **kwargs)

class PackagePurchaseHistory(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='user')
    payment_id = models.CharField(max_length=255, default='')
    package = models.ForeignKey(PackageName, on_delete=models.CASCADE, blank=True, null=True, related_name='package')
    amount = models.FloatField(default=0)
    isConfirmationMailSent = models.BooleanField(default=False, blank=True, null=True)
    purchased_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.user.fname + ' ' + self.user.lname + ' || ' + self.user.email

class Message(models.Model):
    email = models.CharField(default='', max_length=255)
    text = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class PerpetualGrowthRateData(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True, related_name='current_user')
    date = models.CharField(max_length=255)
    symbol = models.CharField(max_length=255)
    symbol_name = models.CharField(max_length=255)
    symbol_currency = models.CharField(max_length=255)
    revenue_ttm = models.CharField(max_length=255)
    nop_ttm = models.CharField(max_length=255)
    roe = models.CharField(max_length=255)
    roc = models.CharField(max_length=255)
    ke = models.CharField(max_length=255)
    kd = models.CharField(max_length=255)
    ev = models.CharField(max_length=255)
    wacc = models.CharField(max_length=255)
    market_cap = models.CharField(max_length=255)
    perpetual_growth_rate = models.CharField(max_length=255)
    de_ratio = models.CharField(max_length=255)
    beta = models.CharField(max_length=255)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.symbol + ' ' + self.symbol_name


