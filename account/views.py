# account.views

from rest_framework import viewsets
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import CombinedUserPersonSerializer
from django.contrib.auth import get_user_model

User  = get_user_model()

class CombinedUserProfileViewSet(RetrieveModelMixin, UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = CombinedUserPersonSerializer
    
    def get_queryset(self):
        # Allow only the user or admin to access their profile
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(user, data=request.data, partial=request.method == 'PATCH')
            serializer.is_valid(raise_exception=True)
            self.update_user_profile(user, serializer.validated_data)
            return Response(serializer.data)

    def update_user_profile(self, user, validated_data):
        # Handle nested person data
        person_data = validated_data.pop('person', {})

        # Update the user instance
        user = super().update(user, validated_data)

        # Update the person instance if it exists
        person = user.person
        if person_data:
            for attr, value in person_data.items():
                setattr(person, attr, value)
            person.save()

        return user