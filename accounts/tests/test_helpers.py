from rest_framework.test import APIClient
import factory
from .account_factory import UserFactory
from abstract.tests.test_helper import TestHelper
from rest_framework import status

class AccountTestHelperFactory(TestHelper):

    @classmethod
    def setUpTestData(self) -> None:

        self.client = APIClient()
        self.new_user = factory.build(dict, FACTORY_CLASS=UserFactory)
        self.new_user['password2'] = self.new_user.get('password')
        self.test_password = UserFactory.raw_password

    def tearDown(self) -> None:
        return super().tearDown()
    
    def get_user(self):
        return UserFactory.create()
    
    def assert_201_created(self, response, err_msg=""):
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, err_msg)
    
    def assert_200_ok(self, response, err_msg=''):
        self.assertEqual(response.status_code, status.HTTP_200_OK, err_msg)

    def assert_400_bad(self, response, err_msg=""):
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, err_msg)

    def assert_401_unauthorized(self, response, err_msg=''):
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, err_msg)