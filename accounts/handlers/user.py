from django.contrib.sites.requests import RequestSite
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest
from django.urls import reverse

from typing import Dict, Tuple, Optional, Any
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AbstractBaseUser
from accounts.handlers.abstract import Handler
from accounts.models import Refferal, User

from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.db.models import Q

import pendulum
import secrets
import hashlib

from accounts.tasks import send_password_recovery_mail
from wallets.models import Cryptocurrency, Wallet

class AccountHandlerFactory(object):

    @staticmethod
    def get(endpoint: str) -> Handler:
        
        endpoint_handlers = {
            "home": HomePageHandler,
            "create_user": CreateUserHandler,
            "password_recovery": PasswordRecoveryHandler
        }

        return endpoint_handlers[endpoint]()

class HomePageHandler(object):

    def get_homepage_data(self, owner: AbstractBaseUser) -> Dict[str, Any]:

        top_ten_crypto = self.get_top_ten()
        user_wallet = self.get_user_wallet(owner)

        return self.response(owner, top_ten_crypto, user_wallet)
    
    def get_top_ten(self):
        return Cryptocurrency.objects.filter(high_ranking=True)
    
    def get_user_wallet(self, owner: AbstractBaseUser) -> Wallet:
        return Wallet.objects.get(owner=owner)
    
    def response(self, owner: AbstractBaseUser, all_top_ten_ranked, wallet: Wallet) -> Tuple[Dict[str, Any], str]:
        data = {
            "owner": owner,
            "wallet": wallet,
            "coins": []
        }

        for coin in all_top_ten_ranked:
            data["coins"].append(coin)

        return data, None
    
    @staticmethod
    def search(keyword: str) -> Dict[str, Any]:
        if not keyword:
            return [], None
        
        results = Cryptocurrency.objects.filter(Q(name__icontains=keyword) | Q(symbol__icontains=keyword))
        coins = []
        for result in results:
            result_data = result.__dict__
            result_data.pop("_state")
            coins.append(result_data) 
        print(coins)
        return coins, None
        

class CreateUserHandler(Handler):

    def run(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        
        data, errors = self.validate(data)
        if errors:
            return data, errors
        
        data, extra_fields = self.transform(data)

        data = self.create(data)
        self.check_refferal(data.get('user'), extra_fields.get("refferal_code"))

        return self.response(data)
    
    def validate(self, data: Dict[str, Any], **kwargs) -> Tuple[Dict[str, Any], str]:
        return data, None
    
    def transform(self, data: Dict[str, Any], **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:

        extra_fields = {}

        if data.get('refferal_code'):
            ref = data.pop('refferal_code')
        
            extra_fields['refferal_code'] = ref

        return data, extra_fields

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user = User.objects.create_user(**data)
        # data["user"] = user.dict()
        data["user"] = user

        return data
    
    def check_refferal(self, user: AbstractBaseUser, refferal_code: str) -> None:

        print(refferal_code)
        if not refferal_code:
            return None
        
        ref = Refferal.objects.get(code=refferal_code)
        reffered_by = ref.owner

        # credit them $10 for refferal
        ref.owner.account.balance += 10
        ref.owner.account.save()

        user.reffered_by = reffered_by
        user.save()

    @staticmethod
    def get_token(user: AbstractBaseUser) -> str:
        token = Token.objects.create(user=user)
        return token
    
    def response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return data, None
    

class PasswordRecoveryHandler(Handler):

    def run(self, data: Dict[str, Any], **kwargs)-> Dict[str, Any]:

        data = self.transform(data) # do nun
        data, errors = self.validate(data) # check that the account is not suspended...

        if errors:
            return data, errors
        
        self.send_recovery_email(data, **kwargs)
        return self.response(data)
    
    def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:

        email = data.get("email")
        user = User.objects.get(email=email)
        data["user"] = user
        return data
    
    def validate(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], None]:

        user = data.get("user")
        # check that it's not a superuser
        if user.is_superuser:
            return data, {"user": "Unauthorized resource"}
        
        return data, None # for now
    
    def send_recovery_email(self, data: Dict[str, Any], **kwargs) -> None:

        user: AbstractBaseUser = data.get("user")
        user_id = urlsafe_base64_encode(force_bytes(user.id))
        email_recovery_url = reverse("accounts:verify-reset-password", kwargs={"uid": user_id})

        user.active_password_reset_link = True
        user.password_reset_key_expires = pendulum.now("UTC").add(minutes=5)
        user.save()

        recovery_url = self._generate_recovery_url(email_recovery_url, **kwargs)
        context = {
            "request": kwargs.get("request"),
            "user": user,
            "recovery_url": recovery_url,
        }
        email: str = user.email
        subject: str = "Recover Password"
        message: str = render_to_string("accounts/recover-password-email.html", context)
        send_password_recovery_mail.delay(subject, message, email)

    def _get_request_data(self, request: HttpRequest) -> Tuple[str]:
        url: RequestSite = get_current_site(request)
        return url.domain, request.scheme
    
    def _generate_recovery_url(self, url_path: str, **kwargs) -> str:
        domain, scheme = self._get_request_data(kwargs.get("request")) 
        url: str = "%s://%s%s"%(scheme, domain, url_path)
        return url
    
    def generate_token(self, uid: str) -> Tuple[Dict[str, str], bool]:
        
        try:
            user_id: str = force_str(urlsafe_base64_decode(uid))
            user: AbstractBaseUser = User.objects.get(id=user_id)
        except (OverflowError, TypeError, ValueError, User.DoesNotExist):
            return None, True
        
        # check to see if the link has been redeemed/key has not expired
        if not user.active_password_reset_link or user.password_reset_key_expires < pendulum.now():
            return None, True
        user.active_password_reset_link = False
        # generate a token using secrets.urlsafe
        password_token = secrets.token_urlsafe(50)
        # hash it
        token_hash = hashlib.sha256(password_token.encode("utf-8")).hexdigest()
        # assign to user.password_reset_key
        user.password_reset_key = token_hash
        # user.password_reset_key_expires = pendulum.now("UTC").add(minutes=5)
        user.save()

        # generate the url using reverse and the genrate_recovery_url method
        url_path = reverse("accounts:reset-password", kwargs={"token": password_token})
        # return the url in a response dict to be used by the template
        context_data = {
            "reset_password_url": url_path
            }
        return context_data, False
    
    def verify(self, token: str) -> AbstractBaseUser:
        # get the token
        # hash it 
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        # compare with hashed value in the db (query which user has an identical hash) AND check the expiry
        try:
            user = User.objects.get(password_reset_key=token_hash)
        except (OverflowError, TypeError, ValueError, User.DoesNotExist):
            return None
         
        if user.password_reset_key_expires < pendulum.now():
            return None
        
        # delete the value form db
        user.password_reset_key = None
        user.save()
        return user

    def reset_password(self, data: Dict[str, Any], token: str) -> Tuple[Dict[str, str], bool]:
        user = self.verify(token)
        if not user:
            return None, True
        
        password = data.get("password")
        user.set_password(password)
        user.save()
        return {}, False

    def response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return data, None