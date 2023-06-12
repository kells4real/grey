from wallet.models import Wallet
from rest_framework import views, viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404, RetrieveUpdateAPIView
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import PiggySerializer, PiggyCrudSerializer
from rest_framework.decorators import api_view, permission_classes
from .models import Piggy
from authentication.models import User
from authentication.utils import Util
from pagination.pagination import StandardPagination
from django.db.models.functions import TruncMonth
from django.db.models.aggregates import Count, Sum
from fcm_django.models import FCMDevice
from notifications.signals import notify
from django.utils import timezone


class PiggyViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, ]
    serializer_class = PiggyCrudSerializer

    def create(self, request):
        if request.user.is_user:
            piggies = Piggy.objects.filter(user=request.user)
            try:
                if piggies.count() < 3:
                    serializer = self.serializer_class(data=request.data, context={"request": request})
                    serializer.is_valid(raise_exception=True)
                    if (serializer.validated_data['frequency'] == 'Weekly' and
                        serializer.validated_data['duration'] >= 12) or (
                            serializer.validated_data['frequency'] == 'Monthly' and
                            serializer.validated_data['duration'] >= 3):
                        piggy = serializer.save(user=request.user)
                        wallet = Wallet.objects.get(user=piggy.user)
                        if wallet.balance >= piggy.save_amount:
                            wallet.balance -= piggy.save_amount
                            piggy.amount_saved += piggy.save_amount
                            piggy.status = 1
                            wallet.save(update_fields=["balance"])
                            piggy.save(update_fields=["amount_saved", "status"])
                        dict_response = {"error": False, "message": "Piggy Created Successfully"}
                        stat = status.HTTP_201_CREATED
                else:
                    dict_response = {"error": True}
                    stat = status.HTTP_403_FORBIDDEN
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request, pk=None):
        try:
            queryset = Piggy.objects.all()
            piggy = get_object_or_404(queryset, pk=pk)
            serializer = PiggySerializer(piggy, many=False)
            response = serializer.data
        except:
            response = status.HTTP_404_NOT_FOUND
        return Response(response)

    def adminList(self, request):
        if request.user.is_staff or request.user.is_admin:
            try:
                piggies = Piggy.objects.all().order_by('-date')
                if piggies.count() > 0:
                    paginator = StandardPagination()
                    result_page = paginator.paginate_queryset(piggies, request)
                    serializer = PiggySerializer(result_page, many=True)

                    response = paginator.get_paginated_response(serializer.data)
                else:
                    response = Response({})

            except:
                response = Response(status.HTTP_404_NOT_FOUND)
            return response

    def destroy(self, request, pk=None):
        user = request.user
        queryset = Piggy.objects.all()
        piggy = get_object_or_404(queryset, pk=pk)
        if user.is_user and piggy.user == user:
            try:
                wallet = Wallet.objects.get(user=user)
                wallet.balance += piggy.amount_saved
                wallet.save(update_fields=["balance"])
                # Send a message to the user to this effect here
                email_body = f"Hi {user.username}, your savings of ${piggy.amount_saved} has been added to " \
                             f"your wallet. " \
                             f"Thank you for saving with Trix Fx. " \
                             f" Have a wonderful day. \n "
                data = {'email_body': email_body, 'to_email': user.email,
                        'email_subject': 'Your Trix Savings'}
                Util.send_email(data)

                piggy.delete()
                dict_response = {"error": False, "message": "Piggy Deleted"}
                stat = status.HTTP_200_OK
            except:
                dict_response = {"error": True}
                stat = status.HTTP_403_FORBIDDEN
            return Response(dict_response, status=stat)
        else:
            return Response({"message": "User is not authorized"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def runningPiggies(request):
    user = request.user
    if user.is_user:
        try:
            piggies = Piggy.objects.filter(user=user).order_by('-date')
            serializer = PiggySerializer(piggies, many=True)
            response = serializer.data
        except:
            response = status.HTTP_404_NOT_FOUND
        return Response(response)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

# Make sure you update settings, crons, wallet.view, investment view configuration model and loan view when
# updating the online code
