from django.urls import path
from .views import HomeView, ResgisterUserView, LoginView, PasswordRecoveryView

app_name: str = 'accounts'

forgot_password = PasswordRecoveryView.as_view({"get": "forgot_password"})
password_reset_validate_email = PasswordRecoveryView.as_view({"post": "password_reset_validate_email"})
verify_reset_password = PasswordRecoveryView.as_view({"get": "verify_reset_password"})
reset_password = PasswordRecoveryView.as_view({"post": "reset_password"})

home = HomeView.as_view({"get": "get_home"})
search = HomeView.as_view({"post": "search"})

urlpatterns = [
    path("dashboard/", home, name="home"),
    path("dashboard/search/", search, name="search-coin"),
    path('register-user/', ResgisterUserView.as_view(), name="register-user"),
    path('register-user/<str:refferal_code>/', ResgisterUserView.as_view(), name="register-user-refferal"),
    path('login/', LoginView.as_view(), name="login"),

    path("forgot-password/", forgot_password, name="forgot-password"),
    path("password-reset-validate-email/", password_reset_validate_email, name="password-reset-validate-email"),
    path("verify-reset-password/<uid>/", verify_reset_password, name="verify-reset-password"),
    path("reset-password/<token>/", reset_password, name="reset-password"),
]