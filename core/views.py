from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.utils import timezone
from .EmailThread import EmailThreading

from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser

from .APIs.serializers import *
from user.models import Account, ProfileImage
from .models import *
from django.db.models import Q
from django.conf import settings
import os
import json
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.http import Http404, HttpResponse
import datetime
from yahoo_fin import stock_info as si
from .check_yahoo_symbool import symbol_found
from .getPerpetualGrowthRateData import calculate_costOfEquity, calculate_costOfDebt, estimate_growth_rate

import stripe
# This is your test secret API key.
stripe.api_key = 'sk_test_tWChqwtM920Q34mlu8VPNroB'



# checking symbool
class IsSymboolOkay(APIView):

    def post(self, request):

        symbol = symbol_found(request.data['epgSymbol'])

        if symbol:
            return Response({"success": "Symbool found!"})
        return Response({"failed": "Symbol not found!"})



class AllUsersAccountView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Account.objects.all()
    serializer_class = UserAccountListSerializer

class AccountDetailsView(APIView):

    # permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = Account.objects.get(userID=user_id)
        serializer = UserAccountListSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

# create account view
class CreateAccountView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):

        user_info = request.data
        serializer = CreateUserSerializer(data=user_info)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, {'Error': 'User already exists!'})
        return Response(serializer.errors)

# package item list view
class PackageItemListView(generics.ListAPIView):
    queryset = PackageItems.objects.all()
    serializer_class = PackageItemSerializer

# package list view
class PackageListView(generics.ListAPIView):
    queryset = PackageName.objects.all()
    serializer_class = PackageNameSerializer

class PackageDetailsView(APIView):
    def get(self, request, package_id):
        package = PackageName.objects.get(package_id=package_id)
        serializer = PackageNameSerializer(package)
        return Response(serializer.data, status=status.HTTP_200_OK)

# package purchase history view
class PackagePurchaseHistoryView(APIView):
    def get(self, request):
        history = PackagePurchaseHistory.objects.all()
        serializer = PackagePurchaseHistorySerializer(history, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):

        user_id = request.data['user_id']
        package_id = request.data['package_id']
        isConfirmationMailSent = request.data['isConfirmationMailSent']
        paymentID = request.data['payment_id']

        if user_id and package_id:
            user = Account.objects.get(userID=user_id)
            package = PackageName.objects.get(pk=package_id)
            info = {'user': user.pk, 'package': package.pk, 'amount': package.price, 'payment_id': paymentID, 'isConfirmationMailSent': isConfirmationMailSent}
        serializer = PackagePurchaseHistorySerializer(data=info)
        if serializer.is_valid():
            serializer.save()   

            # update user account membership status
            user.is_paid_member = True
            user.membershipStartingDate = datetime.datetime.now()
            user.membershipEndingDate = datetime.datetime.now() + datetime.timedelta(days=30)
            user.save()

            # sending confirmation mail
            subject = f"Payment Confirmation & Invoice"
            html_content = render_to_string('invoice.html', context={'amount': package.price, 'payment_id': paymentID, 'user': user})
            email = EmailMessage(subject, html_content, to=[user.email])
            email.content_subtype = 'html'
            # email.send()
            EmailThreading(email).start()

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



def calculate_order_amount(items):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    package = PackageName.objects.filter(package_id=items['id']).first()
    price = str(int(package.price)) + '00'
    return price

# payment view
class PaymentView(APIView):

    def post(self, request):
        try:
            # data = json.loads(request.data)
            data = request.data
            # Create a PaymentIntent with the order amount and currency
            intent = stripe.PaymentIntent.create(
                amount=calculate_order_amount(data['items']),
                currency='sgd',
                # automatic_payment_methods={
                #     'enabled': True,
                # },
                payment_method_types=["card"],
            )
            return Response({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return Response({'Error': 'Unable to show'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# message view
class MessageView(APIView):

    def get(self, request):
        messages = Message.objects.all()
        serializer = UserMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, {'Error': 'Failed to send your message. Try again!'})


class ChangePasswordView(APIView):

    def get_object(self, user_id):
        try:
            return Account.objects.get(userID=user_id)
        except Account.DoesNotExist:
            raise Http404

    def put(self, request, user_id):
        user = self.get_object(user_id)
        serializer = ChangePasswordSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"Success": "Password updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPassword(APIView):

    def post(self, request):
        email_or_username = request.data['email_or_username']
        user = Account.objects.filter(Q(username=email_or_username) | Q(email=email_or_username)).first()

        if user:
            try:
                new_1_time_password = get_random_string(10)
                user.set_password(new_1_time_password)
                user.save()
                # sending confirmation mail
                subject = f"One Time Password - Mavenpolis Partners Pte Ltd"
                html_content = render_to_string('one-time-password.html',
                                                context={'one_time_pass': new_1_time_password, 'user': user})
                email = EmailMessage(subject, html_content, to=[user.email])
                email.content_subtype = 'html'
                # email.send()
                EmailThreading(email).start()

                return Response("Sent an one time password to your mail. Please don't forget to change it after login.")
            except:
                return Response('Unable to accept your request. Try again!')
        else:
            return Response("Wrong username or email!")


class UploadProfileImageView(APIView):

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if request.data['img'] and request.data['user']:

            currnet_user = Account.objects.get(userID=request.data['user'])
            profile_pic_info = {'user': currnet_user.pk, 'img': request.data['img']}

            isUserProfilePicExist = ProfileImage.objects.filter(user=currnet_user).first()

            if isUserProfilePicExist:
                fs = FileSystemStorage()
                fs.delete(isUserProfilePicExist.img.name)
                isUserProfilePicExist.delete()
                serializer = ProfileImageUploadSerializer(data=profile_pic_info)
                if serializer.is_valid():
                    serializer.save()
                    return Response("Successfully updated!")
                else:
                    return Response(serializer.errors)
            else:
                serializer = ProfileImageUploadSerializer(data=profile_pic_info)
                if serializer.is_valid():
                    serializer.save()
                    return Response("Successfully updated!")
                else:
                    return Response(serializer.errors)
        else:
            return Response("User ID and profile image need to be included!")

class Unsubscribe(APIView):

    def post (self, request, username):

        if request.data and request.data['unsubscribe'] and request.data['username']:
            user = Account.objects.filter(userID=request.data['username']).first()
            user.is_paid_member = False
            user.save()
            return Response('Successfully unsubscribed!')


class StartFreeTrialView(APIView):

    def post(self, request, userID):
        if request.data:
            user = Account.objects.get(userID=userID)
            if user:
                user.is_free_trial_used = True
                user.is_paid_member = True
                user.membershipStartingDate = datetime.datetime.now()
                user.membershipEndingDate = datetime.datetime.now() + datetime.timedelta(seconds=15)
                user.save()
                return Response({'success':"Congratulations! Your 7-days free trial has been started!"})
            else:
                return Response({'error': "Your 7-days free trial can't be activated! Try again please!"})
        else:
            return Response({'error': "Your 7-days free trial can't be activated! Try again please!"})


class GetPerpetualGrowthCostOfEquity(APIView):

    def post(self, request):
        cost_of_equity = calculate_costOfEquity(request.data['symbol'], float(request.data['crp']), float(request.data['comRP']))
        return Response(cost_of_equity)


class GetPerpetualCostOfDebt(APIView):

    def post(self, request):
        cost_of_debt = calculate_costOfDebt(request.data['symbol'], request.data['rating'], float(request.data['premium']))
        return Response(cost_of_debt)

class GetPerpetualGrowthRateView(APIView):

    def post(self, request, userID):
        user = Account.objects.filter(userID=userID).first()
        print(request.data)
        estimateGrowthRate = estimate_growth_rate(request.data['symbol'], float(request.data['crp']), float(request.data['comRP']), request.data['rating'], float(request.data['premium']))
        if user and estimateGrowthRate:
            perpetualGrowthRateToStore = PerpetualGrowthRateData(
            user=user,
            date = estimateGrowthRate['date'],
            symbol = estimateGrowthRate['symbol'],
            symbol_name = estimateGrowthRate['symbol_name'],
            symbol_currency = estimateGrowthRate['symbol_currency'],
            revenue_ttm = estimateGrowthRate['revenue_ttm'],
            nop_ttm = estimateGrowthRate['nop_ttm'],
            roe = estimateGrowthRate['roe'],
            roc = estimateGrowthRate['roc'],
            ke = estimateGrowthRate['ke'],
            kd = estimateGrowthRate['kd'],
            ev = estimateGrowthRate['ev'],
            wacc = estimateGrowthRate['wacc'],
            market_cap = estimateGrowthRate['market_cap'],
            perpetual_growth_rate = estimateGrowthRate['perpetual_gowth_rate'],
            de_ratio = estimateGrowthRate['de_ratio'],
            beta = estimateGrowthRate['beta'],
            )
            perpetualGrowthRateToStore.save()
        print(estimateGrowthRate)
        return Response(estimateGrowthRate)


class GetPerpetualGrowthRateHistoryView(APIView):

    def get(self, request):
        history = PerpetualGrowthRateData.objects.all()
        serilizer = PerpetualGrowthRateHistorySerializer(history, many=True)

        return Response(serilizer.data, status=status.HTTP_200_OK)
# {
#     'date': '16-Sep-2022',
#     'symbol': 'aapl',
#     'symbol_name': 'Apple Inc.',
#     'symbol_currency': 'USD',
#     'revenue_ttm': 387542.0,
#     'nop_ttm': 101983.0,
#     'roe': 1.714647116526408,
#     'roc': 0.5735891292365494,
#     'ke': 0.2081,
#     'kd': 0.0948,
#     'ev': 2701460.0,
#     'wacc': 0.13182810549050045,
#     'market_cap': 2630000.0,
#     'perpetual_gowth_rate': 0.0393,
#     'de_ratio': 2.059837885280603,
#     'beta': 1.23
# }







