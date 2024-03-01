from django.http.request import HttpRequest
from django.http.response import JsonResponse
from rest_framework.views import APIView, Response
from rest_framework import viewsets
from rest_framework import permissions, authentication
from rest_framework.renderers import TemplateHTMLRenderer
from .serializers import CoinSerializer, WalletSerializer
from .handlers.wallet import WalletHandlerFactory
from rest_framework import status


class WalletView(viewsets.ModelViewSet):

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication]
    renderer_classes = [TemplateHTMLRenderer]

    def get_wallet(self, request:HttpRequest) -> Response:
        handler = WalletHandlerFactory.get("get_wallet")
        data, error = handler.run(request.user)

        if error:
            return JsonResponse({"error": "Wallet does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data, template_name="wallets/wallet_detail.html", status=status.HTTP_200_OK)
    
    def add_coin(self, request: HttpRequest, coin_id: str) -> Response:

        amount = request.POST.dict().get("amount")
        handler = WalletHandlerFactory.get("add_coin")
        data, error = handler.run(request.user, coin_id, amount)
        
        if error:
          return JsonResponse({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data, template_name="wallets/wallet_detail.html", status=status.HTTP_200_OK)

    def remove_coin(self, request: HttpRequest, coin_id: str) -> Response:

        handler = WalletHandlerFactory.get("remove_coin")
        data, error = handler.run(request.user, coin_id)
        
        if error:
          return JsonResponse({"error": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data, template_name="wallets/wallet_detail.html", status=status.HTTP_200_OK)

