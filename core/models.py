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

