from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.db import transaction

User = get_user_model()

# Helos is from attack on titan (idk, name looks cool) 

class UserTestCase(TestCase):
    
    def test_create_user_with_email(self):

        user = None

        user = User.objects.create_user(
            first_name="Helos",
            last_name="Melly",
            email="test@user.com",
            password="foo"
        )

        self.assertIsNotNone(user)

        self.assertEqual(user.first_name, "Helos")
        self.assertEqual(user.last_name, "Melly")
        self.assertEqual(user.email, "test@user.com")
        

    def test_cannot_create_user_without_email(self):

        user = None

        with self.assertRaises(ValueError):     
            User.objects.create_user(
                first_name="Helos",
                last_name="Melly",
                password="foo"
            )

        with self.assertRaises(ValueError):     
            User.objects.create_user(
                first_name="Helos",
                last_name="Melly",
                email="",
                password="foo"
            )


    def test_cannot_create_user_without_both_first_and_last_name(self):

        user = None

        with self.assertRaises(ValueError):     
            User.objects.create_user(
                first_name="",
                last_name="Melly",
                email="test@mail.com",
                password="foo"
            )

        with self.assertRaises(ValueError):     
            User.objects.create_user(
                first_name="Helos",
                last_name="",
                email="test@mail.com",
                password="foo"
            )

        with self.assertRaises(ValueError):     
            User.objects.create_user(
                first_name="",
                last_name="",
                email="test@mail.com",
                password="foo"
            )

    def test_cannot_create_user_with_existing_email(self):

        user = None

        user = User.objects.create_user(
            first_name="Helos",
            last_name="Melly",
            email="test@user.com",
            password="foo"
        )

        self.assertIsNotNone(user)

        with self.assertRaises(IntegrityError) as context:

            with transaction.atomic():
                User.objects.create_user(
                    first_name="Helos",
                    last_name="Melly",
                    email="test@user.com",
                    password="foo",
                )

        # test should pass and not throw IntegrityError
        User.objects.create_user(
            first_name="Helos",
            last_name="Melly",
            email="test@mail.com",
            password="foo",
        )

        self.assertEqual(User.objects.count(), 2)


        