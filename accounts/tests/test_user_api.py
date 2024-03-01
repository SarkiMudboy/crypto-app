from django.http import response

from crypto_app.abstract.tests.test_helper import TestHelper
from crypto_app.accounts.models import UserAccount
from crypto_app.wallets.models import Wallet
from .test_helpers import AccountTestHelper

from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch

from ..tasks import send_password_recovery_mail

REGISTER_USER = reverse('accounts:register-user')
LOGIN = reverse('accounts:login')
DASHBOARD = reverse('accounts:home')

User = get_user_model()

class SignUpTestCase(AccountTestHelper):

    def test_can_create_user(self):
        new_user = self.new_user
        response = self.client.post(REGISTER_USER, new_user, format='json')
        self.assert_201_created(response, 'User not created')

    def test_cannot_create_user_without_first_and_last_name(self):

        new_user = self.new_user.copy()
        
        new_user.pop("first_name")
        new_user.pop("last_name")
        response = self.client.post(REGISTER_USER, new_user, format='json')
        self.assert_400_bad(response, 'User was created without first and last name')

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(email=new_user.get('email'))

        new_user = self.new_user.copy()

        new_user.pop("first_name")
        response = self.client.post(REGISTER_USER, new_user, format='json')
        self.assert_400_bad(response, 'User was created without first name')

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(first_name=new_user.get('first_name'))

        new_user = self.new_user.copy()

        new_user.pop("last_name")
        response = self.client.post(REGISTER_USER, new_user, format='json')
        self.assert_400_bad(response, 'User was created without last name')

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(last_name=new_user.get('last_name'))

    def test_cannot_create_user_without_email_or_phone(self):
        
        new_user = self.new_user
        new_user.pop("email")

        response = self.client.post(REGISTER_USER, new_user, format='json')
        self.assert_400_bad(response, 'User was created without email')

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(first_name=new_user.get("first_name"))

    def test_wallet_and_account_are_created_after_sign_up(self):
        new_user = self.new_user
        response = self.client.post(REGISTER_USER, new_user, format='json')
        self.assert_201_created(response, 'User not created')
        user = User.objects.get(email=new_user.get("email"))

        wallet = Wallet.objects.filter(owner=user)
        assert wallet.exists() is True

        account = UserAccount.objects.filter(owner=user)
        assert account.exists() is True

    def test_password_not_included_in_register_response(self):
        user_data = self.user_data
        response = self.client.post(path=REGISTER_USER, data=user_data, format='json')
        self.assertNotIn('password', response.json())

    def test_sign_up_redirects_to_dashboard(self):

        new_user = self.new_user
        response = self.client.post(REGISTER_USER, new_user, format='json')
        self.assert_201_created(response, 'User not created')
        self.assertRedirects(response, DASHBOARD)


class LoginTestCase(AccountTestHelper):

    def test_cannot_login_without_crredentials(self):
        response = self.client.post(LOGIN, {}, format='json')
        self.assert_400_bad(response)

    def test_user_can_login_with_correct_credentials(self):
        # test user can login
        user_data = self.get_user()
        login_data = {'email': user_data.email, 'password': self.test_password}

        response = self.client.post(LOGIN, data=login_data, format='json')
        self.assert_200_ok(response)
        self.assertRedirects(response, DASHBOARD)


class DashboardTestCase(TestHelper):

    def test_user_can_see_wallet_and_top_ten_crypto_in_dashboard(self):

        user_data = self.get_user()
        login_data = {'email': user_data.email, 'password': self.test_password}

        response = self.client.post(LOGIN, data=login_data, format='json')
        self.assert_200_ok(response)
        self.assertRedirects(response, DASHBOARD)

        self.assertIsNotNone(response.json().get("wallet"))
        self.assertIsNotNone(response.json().get("coins"))

        # coins = response.json().get("coins")



