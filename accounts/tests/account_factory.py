import factory
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(lambda user: "%s_%s@examplemail.com" %(user.first_name, user.last_name))
    password = 'its-a-secret'

    @property
    def raw_password(self):
        return "its-a-secret"