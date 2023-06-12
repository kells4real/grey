from django.shortcuts import render
from rest_framework import views, viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, RetrieveUpdateAPIView
from rest_framework import status
from authentication.utils import Util
from compression_middleware.decorators import compress_page
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import PortfolioSerializer, InvestmentSerializer, InvestSerializer, AdminInvestmentSerializer, \
    ReferralSerializer, ProfitSerializer, SoldInvestmentSerializer
from .models import Portfolio, Investment, Profit, SoldInvestment
from rest_framework.decorators import api_view, permission_classes
from authentication.models import User
from wallet.models import Wallet, AddToWallet, WalletTransfer, Withdraw
from wallet.serializers import WalletTransferSerializer, WithdrawSerializer, AddToWalletSerializer
from django.db.models import Q
from pagination.pagination import StandardPagination, AdminPagination
from django.db.models.functions import TruncMonth
from django.db.models.aggregates import Count, Sum
from account.models import BankAccount
from datetime import datetime
from django.utils import timezone
from piggyvest.models import Piggy


class PortfolioViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]
    serializer_class = PortfolioSerializer

    def create(self, request):
        if self.request.user.is_admin:
            try:
                serializer = self.serializer_class(data=request.data, context={"request": request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                dict_response = {"error": False, "message": "Portfolio Created Successfully"}
                stat = status.HTTP_201_CREATED
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request, pk=None):
        try:
            queryset = Portfolio.objects.all()
            portfolio = get_object_or_404(queryset, pk=pk)
            serializer = self.serializer_class(portfolio, many=False)
            response = serializer.data
        except:
            response = status.HTTP_404_NOT_FOUND
        return Response(response)

    def update(self, request, pk=None):
        if self.request.user.is_admin:
            try:
                queryset = Portfolio.objects.all()
                portfolio = get_object_or_404(queryset, pk=pk)
                serializer = self.serializer_class(portfolio, data=request.data, context={"request": request})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                dict_response = {"error": False, "message": "Updated Portfolio Successfully"}
                stat = status.HTTP_200_OK
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, pk=None):
        if self.request.user.is_admin:
            try:
                queryset = Portfolio.objects.all()
                portfolio = get_object_or_404(queryset, pk=pk)
                portfolio.delete()
                dict_response = {"error": False, "message": "Deleted Portfolio Successfully"}
                stat = status.HTTP_200_OK
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)


# All portfolios
@api_view(["GET"])
def portfolios(request):
    categories = Portfolio.objects.all()
    serializer = PortfolioSerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class InvestViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]

    def list(self, request):
        if request.user.is_user:
            investments = Investment.objects.filter(user=request.user)
            serializer = InvestmentSerializer(investments, many=True)
            totalInvestments = sum(investments.filter(disabled=False).values_list('amount', flat=True))
            totalSaved = sum(Piggy.objects.filter(user=request.user).values_list('amount_saved', flat=True))
            profit = Profit.objects.filter(user=request.user)
            totalProfit = sum(profit.values_list('amount', flat=True))
            wallet = Wallet.objects.get(user=request.user)
            referrals = User.objects.filter(referee=request.user)
            refs = AddToWallet.objects.filter(user=request.user, type="Referral")
            referralBonus = sum(refs.values_list('amount', flat=True))
            projectedProfitMonthly = sum([investment.interest() for investment in investments
                                          if investment.portfolio.profit_frequency == "Monthly"]) * 12
            projectedProfitWeekly = sum([investment.interest() for investment in investments
                                         if investment.portfolio.profit_frequency == "Weekly"]) * 52
            projectedProfit = projectedProfitMonthly + projectedProfitWeekly
            withdraws = Withdraw.objects.filter(user=request.user, approved=True).order_by('-date')[:3]
            transfers = WalletTransfer.objects.filter(Q(user_from=request.user) |
                                                      Q(user_to=request.user)).order_by('-date').distinct()[:3]
            add_wallet = AddToWallet.objects.filter(user=request.user).order_by('-date')[:3]
            if BankAccount.objects.filter(user=request.user, primary=True):
                account = True
            else:
                account = False
            return Response({"investments": serializer.data,
                             "totalInvestments": totalInvestments,
                             "walletBalance": wallet.balance, "totalProfit": totalProfit,
                             "projectedProfit": projectedProfit, "referrals": referrals.count(),
                             "referralBonus": referralBonus, "withdraws": WithdrawSerializer(withdraws, many=True).data,
                             "transfers": WalletTransferSerializer(transfers, many=True).data,
                             "add_wallet": AddToWalletSerializer(add_wallet, many=True).data,
                             "code": request.user.referenceCode, "country": request.user.country,
                             "bitcoin": request.user.bitcoin, "account": account, "total_saved": totalSaved})

        elif request.user.is_admin or request.user.is_staff:
            investments = Investment.objects.filter(sold=False)
            investment = investments.count()
            totalInvestments = sum(investments.values_list('amount', flat=True))
            totalSaved = sum(Piggy.objects.filter(user=request.user).values_list('amount_saved', flat=True))
            profit = Profit.objects.all()
            totalProfit = sum(profit.values_list('amount', flat=True))
            wallets = Wallet.objects.all()
            added = AddToWallet.objects.all()
            sumAdded = sum(added.values_list('amount', flat=True))
            totalWallet = sum(wallets.values_list('balance', flat=True))
            referrals = User.objects.filter(referred=True)
            refs = AddToWallet.objects.filter(type="Referral")
            referralBonus = sum(refs.values_list('amount', flat=True))
            withdraws = Withdraw.objects.filter(approved=True).order_by('-date')[:3]
            transfers = WalletTransfer.objects.all().order_by('-date')[:3]
            add_wallet = AddToWallet.objects.all().order_by('-date')[:3]
            projectedProfitMonthly = sum([investment.interest() for investment in investments
                                          if investment.portfolio.profit_frequency == "Monthly"]) * 12
            projectedProfitWeekly = sum([investment.interest() for investment in investments
                                         if investment.portfolio.profit_frequency == "Weekly"]) * 52
            projectedProfit = projectedProfitMonthly + projectedProfitWeekly
            sumBalance = sumAdded - (referralBonus + totalProfit)
            totalExpenses = referralBonus + totalProfit
            return Response({"investments": investment,
                             "totalInvestments": totalInvestments, "projectedProfit": projectedProfit,
                             "walletBalance": totalWallet, "totalExpenses": totalExpenses,
                             "referrals": referrals.count(), "sumAdded": sumAdded, "sumBalance": sumBalance,
                             "referralBonus": referralBonus, "withdraws": WithdrawSerializer(withdraws, many=True).data,
                             "transfers": WalletTransferSerializer(transfers, many=True).data,
                             "add_wallet": AddToWalletSerializer(add_wallet, many=True).data,  "total_saved": totalSaved})

        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request):
        try:
            serializer = InvestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            portfolio = Portfolio.objects.get(name=serializer.validated_data['portfolio'])
            amount = serializer.validated_data['amount']
            wallet = Wallet.objects.get(user=self.request.user)

            if wallet.balance >= amount >= portfolio.lowest and amount <= portfolio.highest:
                if portfolio:
                    Investment.objects.create(user=self.request.user, portfolio=portfolio, amount=amount)
                    wallet = Wallet.objects.get(user=request.user)
                    wallet.balance -= amount
                    wallet.save(update_fields=["balance"])
                    dict_response = {"error": False, "message": "Investment Created Successfully"}
                    stat = status.HTTP_201_CREATED
                else:
                    dict_response = {"error": True, "message": "Portfolio Not Found."}
                    stat = status.HTTP_404_NOT_FOUND
            else:
                dict_response = {"error": True, "message": "Not Enough Funds In Wallet."}
                stat = status.HTTP_400_BAD_REQUEST
        except:
            dict_response = {"error": True}
            stat = status.HTTP_403_FORBIDDEN
        return Response(dict_response, status=stat)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def adminSummary(request):
    if request.user.is_staff or request.user.is_admin:
        investments = Investment.objects.all()
        totalInvestmentAmount = sum(investments.values_list('amount', flat=True))
        profit = Profit.objects.all()
        totalUsers = User.objects.filter(is_user=True).count()
        totalProfit = sum(profit.values_list('amount', flat=True))
        return Response({"totalInvestments": investments.count(), "totalInvestmentAmount": totalInvestmentAmount,
                         "totalProfit": totalProfit, "totalUsers": totalUsers})
    else:
        return Response({"message": "User unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@compress_page
def getReferrals(request):
    user = request.user
    if user.is_user:
        users = User.objects.filter(referee=user).order_by('-date_joined')
        if users.count() > 0:
            paginator = StandardPagination()
            result_page = paginator.paginate_queryset(users, request)
            serializer = ReferralSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        else:
            return Response({}, status=status.HTTP_200_OK)

    if user.is_admin or user.is_staff:
        users = User.objects.filter(is_user=True).order_by('-date_joined')
        if users.count() > 0:
            paginator = AdminPagination()
            result_page = paginator.paginate_queryset(users, request)
            serializer = ReferralSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        else:
            return Response({}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


month = str(datetime.now()).split("-")[1]


@permission_classes([IsAuthenticated])
@api_view(["GET"])
@compress_page
def refs(request):
    user = request.user
    if user.is_user:

        currentMonth = User.objects.filter(referee=user, date_joined__month=month).count()
        previousMonth = User.objects.filter(referee=user, date_joined__month=int(month) - 1).count()
        arrow = ""
        if currentMonth >= previousMonth:
            # print(currentMonth)
            if previousMonth > 0:  # This is to avoid the zero division error
                percentage = ((currentMonth - previousMonth) / previousMonth) * 100
            else:  # This is to avoid the zero division error
                percentage = currentMonth * 100
            arrow = "up"
        else:
            if currentMonth > 0:
                percentage = ((previousMonth - currentMonth) / currentMonth) * 100
            else:
                percentage = previousMonth * 100
            arrow = "down"

        aggregated = User.objects.filter(referee=user).annotate(month=TruncMonth('date_joined')).values(
            'month').annotate(
            sum_by_month=Count('month'))
        return Response({"data": aggregated, "currentMonth": currentMonth, "previousMonth": previousMonth,
                         "percentage": {"percentage": int(percentage), "arrow": arrow}})
    elif user.is_staff or user.is_admin:
        currentMonth = User.objects.filter(referred=True, date_joined__month=month).count()
        previousMonth = User.objects.filter(referred=True, date_joined__month=int(month) - 1).count()
        arrow = ""
        if currentMonth >= previousMonth:
            # print(currentMonth)
            if previousMonth > 0:  # This is to avoid the zero division error
                percentage = ((currentMonth - previousMonth) / previousMonth) * 100
            else:  # This is to avoid the zero division error
                percentage = currentMonth * 100
            arrow = "up"
        else:
            if currentMonth > 0:
                percentage = ((previousMonth - currentMonth) / currentMonth) * 100
            else:
                percentage = previousMonth * 100
            arrow = "down"
        aggregated = User.objects.filter(referred=True).annotate(month=TruncMonth('date_joined')).values(
            'month').annotate(
            sum_by_month=Count('month'))
        return Response({"data": aggregated, "currentMonth": currentMonth, "previousMonth": previousMonth,
                         "percentage": {"percentage": int(percentage), "arrow": arrow}})


@permission_classes([IsAuthenticated])
@api_view(["GET"])
@compress_page
def refBonus(request):
    user = request.user
    if user.is_user:
        currentMonthBonus = AddToWallet.objects.filter(user=user,
                                                       type="Referral", date__month=month)
        previousMonthBonus = AddToWallet.objects.filter(user=user,
                                                        type="Referral", date__month=int(month) - 1)
        totalCurrentMonth = sum(currentMonthBonus.values_list('amount', flat=True))
        totalPreviousMonth = sum(previousMonthBonus.values_list('amount', flat=True))

        currentMonthProfit = sum(Profit.objects.filter(user=user, date__month=month).values_list('amount', flat=True))
        previousMonthProfit = sum(Profit.objects.filter(user=user, date__month=int(month) - 1).values_list('amount',
                                                                                                           flat=True))
        currentMonthTotal = totalCurrentMonth + currentMonthProfit
        previousMonthTotal = totalPreviousMonth + previousMonthProfit

        arrow = ""
        if currentMonthTotal >= previousMonthTotal:
            if previousMonthTotal > 0:
                percentage = ((currentMonthTotal - previousMonthTotal) / previousMonthTotal) * 100
            else:
                percentage = currentMonthTotal * 100
            arrow = "up"
        else:
            if currentMonthTotal > 0:
                percentage = ((previousMonthTotal - currentMonthTotal) / currentMonthTotal) * 100
            else:
                percentage = previousMonthTotal * 100
            arrow = "down"
        referralBonus = AddToWallet.objects.filter(user=user,
                                                   type="Referral").annotate(month=TruncMonth('date')
                                                                             ).values('month').annotate(Sum('amount'))
        aggregatedProfit = Profit.objects.filter(user=user).annotate(month=TruncMonth('date')).values(
            'month').annotate(Sum('amount'))
        newList = []
        for i in aggregatedProfit:
            for e in referralBonus:
                if i["month"] == e["month"]:
                    h = {'month': i["month"], "profit": i["amount__sum"], "bonus": e["amount__sum"]}
                    newList.append(h)
        months = []
        for i in newList:
            # Append all months in newList to months variable
            months.append(i["month"])
        # Check if a month present in aggregatedProfit is not present in months already, add it to the months
        # variable along with bonus being 0 as it means bonus does have data for that month
        for i in aggregatedProfit:
            if i["month"] not in months:
                h = {'month': i["month"], "profit": i["amount__sum"], "bonus": 0}
                months.append(i["month"])  # Append the month the months variable
                newList.append(h)
        # Check if a month present in referralBonus is not present in months already, add it to the months variable
        # along with bonus being 0 as it means profit does have data for that month
        for i in referralBonus:
            if i["month"] not in months:
                h = {'month': i["month"], "profit": 0, "bonus": i["amount__sum"]}
                newList.append(h)
        newList = sorted(newList, key=lambda d: d['month'])  # Sort based on the month
        return Response({"data": newList, "percentage": {"percentage": int(percentage), "arrow": arrow}})

    elif user.is_staff or user.is_admin:
        currentMonthBonus = AddToWallet.objects.filter(type="Referral", date__month=month)
        previousMonthBonus = AddToWallet.objects.filter(type="Referral", date__month=int(month) - 1)
        totalCurrentMonth = sum(currentMonthBonus.values_list('amount', flat=True))
        totalPreviousMonth = sum(previousMonthBonus.values_list('amount', flat=True))

        currentMonthProfit = sum(Profit.objects.filter(date__month=month).values_list('amount', flat=True))
        previousMonthProfit = sum(Profit.objects.filter(date__month=int(month) - 1).values_list('amount', flat=True))
        currentMonthTotal = totalCurrentMonth + currentMonthProfit
        previousMonthTotal = totalPreviousMonth + previousMonthProfit

        arrow = ""
        if currentMonthTotal >= previousMonthTotal:
            if previousMonthTotal > 0:
                percentage = ((currentMonthTotal - previousMonthTotal) / previousMonthTotal) * 100
            else:
                percentage = currentMonthTotal * 100
            arrow = "up"
        else:
            if currentMonthTotal > 0:
                percentage = ((previousMonthTotal - currentMonthTotal) / currentMonthTotal) * 100
            else:
                percentage = previousMonthTotal * 100
            arrow = "down"
        referralBonus = AddToWallet.objects.filter(type="Referral").annotate(month=TruncMonth('date')
                                                                             ).values('month').annotate(Sum('amount'))
        aggregatedProfit = Profit.objects.all().annotate(month=TruncMonth('date')).values(
            'month').annotate(Sum('amount'))
        newList = []
        for i in aggregatedProfit:
            for e in referralBonus:
                if i["month"] == e["month"]:
                    h = {'month': i["month"], "profit": i["amount__sum"], "bonus": e["amount__sum"]}
                    newList.append(h)
        months = []
        for i in newList:
            # Append all months in newList to months variable
            months.append(i["month"])
        # Check if a month present in aggregatedProfit is not present in months already, add it to the months
        # variable along with bonus being 0 as it means bonus does have data for that month
        for i in aggregatedProfit:
            if i["month"] not in months:
                h = {'month': i["month"], "profit": i["amount__sum"], "bonus": 0}
                months.append(i["month"])  # Append the month the months variable
                newList.append(h)
        # Check if a month present in referralBonus is not present in months already, add it to the months variable
        # along with bonus being 0 as it means profit does have data for that month
        for i in referralBonus:
            if i["month"] not in months:
                h = {'month': i["month"], "profit": 0, "bonus": i["amount__sum"]}
                newList.append(h)
        newList = sorted(newList, key=lambda d: d['month'])  # Sort based on the month
        # newList.append({"percentage": })
        return Response({"data": newList, "percentage": {"percentage": int(percentage), "arrow": arrow}})


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def sellInvestment(request, pk):
    user = request.user
    investment = Investment.objects.filter(user=user, id=pk)
    if investment:
        investment = investment[0]
        SoldInvestment.objects.create(user=user, investment=investment)
        investment.disabled = True
        investment.save(update_fields=['disabled'])
        return Response({"success": True}, status=status.HTTP_201_CREATED)
    else:
        return Response({"success": False}, status=status.HTTP_403_FORBIDDEN)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def getProfit(request):
    user = request.user
    if user:
        profits = Profit.objects.filter(user=user).order_by('-date')[:5]
        serializer = ProfitSerializer(profits, many=True)
        return Response(serializer.data)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def updateInvestmentSale(request, pk, param):
    user = request.user
    investment = SoldInvestment.objects.get(id=pk)
    if investment and (user.is_staff or user.is_admin):
        if param == 'approved':
            investment.approved = True
            investment.confirmedBy = user.username
            investment.confirmDate = timezone.now()
            investment.save(update_fields=['approved', 'confirmedBy', 'confirmDate'])
            email_body = f"Hi {user.username}, your portfolio sale of ${investment.amount} " \
                         f"has been approved and funds have been added to " \
                         f"your wallet. " \
                         f"Thank you for investing with Trix Fx. " \
                         f" Have a wonderful day. \n "
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Portfolio Sale Approved'}
            Util.send_email(data)
        elif param == 'declined':
            investment.declined = True
            investment.confirmedBy = user.username
            investment.confirmDate = timezone.localtime().now()
            investment.save(update_fields=['declined', 'confirmedBy', 'confirmDate'])
            email_body = f"Hi {user.username}, your portfolio sale of ${investment.amount} " \
                         f"has been declined. If you feel there is a mistake with this action, " \
                         f"please contact support for quick resolution. " \
                         f"Thank you for investing with Trix Fx. " \
                         f" Have a wonderful day. \n "
            data = {'email_body': email_body, 'to_email': user.email,
                    'email_subject': 'Portfolio Sale Declined'}
            Util.send_email(data)
        return Response({"success": True}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@permission_classes([IsAuthenticated])
@api_view(['GET'])
def investmentSales(request):
    if request.user.is_staff or request.user.is_admin:
        investments = SoldInvestment.objects.all().order_by('-date')
        if investments.count() > 0:
            paginator = AdminPagination()
            result_page = paginator.paginate_queryset(investments, request)
            serializer = SoldInvestmentSerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)
        else:
            return Response({}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)




