# account.urls

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CombinedUserProfileViewSet

router = DefaultRouter()
router.register(r'persons', CombinedUserProfileViewSet, basename='user')

urlpatterns = [
    path(r'', include(router.urls)),
]