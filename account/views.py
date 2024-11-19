# account.views

from rest_framework import viewsets
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import CombinedUserPersonSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CombinedUserProfileViewSet(RetrieveModelMixin, UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = CombinedUserPersonSerializer
    
    def get_queryset(self):
        return User.objects.all()

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(user, data=request.data, partial=request.method == 'PATCH')
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)