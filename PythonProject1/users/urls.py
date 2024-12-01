from django.urls import path
from .views import AuthView, VerifyCodeView, ProfileView, ActivateInviteView

urlpatterns = [
    path('auth/', AuthView.as_view(), name='auth'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('activate-invite/', ActivateInviteView.as_view(), name='activate_invite'),
]
