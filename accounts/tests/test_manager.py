from django.test import TestCase
from django.contrib.auth import get_user_model


class UserManagerTestCase(TestCase):

    def test_create_user(self):

        User = get_user_model()
        user = User.objects.create_user(first_name="John", last_name="Freiza", email="test@user.com", password="foo")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Freiza")
        self.assertEqual(user.email, "test@user.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        try:
            # username: DoesNotExist (AbstractBaseUser)
            self.assertNone(user.username)
        except AttributeError:
            pass

        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(TypeError):
            User.objects.create_user(email="")
        with self.assertRaises(ValueError):
            User.objects.create_user(first_name="", last_name="", email="", password="foo")
        with self.assertRaises(TypeError):
            User.objects.create_user(email="test@usermail.com", password="foo")

    def test_create_superuser(self):

        User = get_user_model()
        superuser = User.objects.create_superuser(first_name="John", last_name="Freiza", email="test@user.com", password="foo")
        self.assertEqual(superuser.email, "test@user.com")
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

        try:
            # username: DoesNotExist (AbstractBaseUser)
            self.assertNone(superuser.username)
        except AttributeError:
            pass

        with self.assertRaises(ValueError):
            User.objects.create_superuser(first_name="", last_name="", email="testsuperuser@mail.com",
                                           password="foo", is_superuser=False)
