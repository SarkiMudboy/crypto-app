from rest_framework import viewsets
from rest_framework import permissions, authentication
from rest_framework.renderers import TemplateHTMLRenderer


class AuthViewSet(viewsets.ModelViewSet):
    
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]
    renderer_classes = [TemplateHTMLRenderer]


class AnonViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    renderer_classes = [TemplateHTMLRenderer]


