from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.utils.crypto import get_random_string



class MyUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email,
            username=username,
            password=password,
        )

        user.is_admin = True
        user.is_a_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user

# all users model to store registered accounts
class Account(AbstractBaseUser):

    options = (
        ('1', 'Verified'),
        ('0', 'Not Verified'),
    )

    userID = models.CharField(max_length=255, default='', blank=True, null=True)
    fname = models.CharField(max_length=255, default='')
    lname = models.CharField(max_length=255, default='')
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    username = models.CharField(verbose_name='username', max_length=50, unique=True)
    phone_no = models.CharField(max_length=255, default='', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_paid_member = models.BooleanField(default=False)
    is_a_staff = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=options, blank=True, null=True, default=0)
    is_agreed_with_termsConsition = models.BooleanField(default=False, blank=True, null=True)
    is_free_trial_used = models.BooleanField(default=False, blank=True, null=True)

    membershipStartingDate = models.DateTimeField(blank=True, null=True)
    membershipEndingDate = models.DateTimeField(blank=True, null=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

# storing profile image/picture of every user
class ProfileImage(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='profile_pic')
    img =  models.ImageField(upload_to='profileImg')

    def __str__(self):
        return self.user.email

