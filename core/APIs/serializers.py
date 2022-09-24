from rest_framework import serializers
from user.models import Account, ProfileImage
from ..models import PackageName, PackageItems, PackagePurchaseHistory, Message, PerpetualGrowthRateData, EstimatedIntrinsicValueData, NumberOfRequestByUser
from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate



# profile image upload serializer
class ProfileImageUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfileImage
        fields = ['user', 'img']

    # to inject foreign key value we have to use "to_representation method instead of create()"
    def to_representation(self, instance):
        self.fields['user'] = UserAcntSerializerForPurchaseHistory(read_only=True)
        return super(ProfileImageUploadSerializer, self).to_representation(instance)

class ProfileImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileImage
        fields = ['img']

class UserAccountListSerializer(serializers.ModelSerializer):

    profile_pic = ProfileImageListSerializer(read_only=True)

    class Meta:
        model = Account
        exclude = ('password',)

# create account serializer
class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'

    def create(self, validated_data):
        user = Account.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.fname = validated_data['fname']
        user.lname = validated_data['lname']
        user.is_active = True
        user.status = '1'
        user.userID = get_random_string(20)
        user.is_agreed_with_termsConsition = True
        user.membership_status = 'free_member'
        user.set_password(validated_data['password'])
        user.save()
        return user


# package items serializer
class PackageItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = PackageItems
        # fields = '__all__'
        fields = ['id', 'item_description']


# package serializers
class PackageNameSerializer(serializers.ModelSerializer):
    items = PackageItemSerializer(many=True) # for many-to-many field use "field name", for foreign key use "related_name"
    class Meta:
        model = PackageName
        fields = '__all__'


class UserAcntSerializerForPurchaseHistory(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ('id', 'email',)

class PackageSerializerForPurchaseHistory(serializers.ModelSerializer):
    class Meta:
        model = PackageName
        fields = ('id', 'name',)



# packge purchase history serializer
class PackagePurchaseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PackagePurchaseHistory
        fields = ['user', 'package', 'amount', 'isConfirmationMailSent', 'payment_id']

    # to inject foreign key value we have to use "to_representation method instead of create()"
    def to_representation(self, instance):
        self.fields['user'] = UserAcntSerializerForPurchaseHistory(read_only=True)
        self.fields['package'] = PackageSerializerForPurchaseHistory(read_only=True)
        return super(PackagePurchaseHistorySerializer, self).to_representation(instance)

# message serializer
class UserMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


# change password serializer
class ChangePasswordSerializer(serializers.ModelSerializer):

    password_new = serializers.CharField(write_only=True, required=True)
    password_old = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = Account
        fields = ["username", "password_old", "password_new"]

    def validate(self, attrs):
        auth = authenticate(username=attrs["username"], password=attrs["password_old"])
        if attrs['password_new'] == attrs['password_old']:
            raise serializers.ValidationError("New password can't be matched with old password!")
        if auth is None:
            raise serializers.ValidationError("User not found!")
        return attrs

    def validate_password_new(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password length must be 8 character long!")
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password_new"])
        instance.save()
        return instance


# perpetual growthrate history serializer
class PerpetualGrowthRateHistorySerializer(serializers.ModelSerializer):
        user = UserAccountListSerializer()
        class Meta:
            model = PerpetualGrowthRateData
            fields = "__all__"



# perpetual growthrate history serializer
class EstimatedIntrinsicValueHistorySerializer(serializers.ModelSerializer):
        user = UserAccountListSerializer()
        class Meta:
            model = EstimatedIntrinsicValueData
            fields = "__all__"

class GetNumberOfRequestByUserSerializer(serializers.ModelSerializer):
    user = UserAccountListSerializer()
    class Meta:
        model = NumberOfRequestByUser
        fields = "__all__"
