
from django.contrib.auth import authenticate
from authentication.models import User
import os
import random
from rest_framework.exceptions import AuthenticationFailed
from cryptography.fernet import Fernet
from wallet.models import Wallet


def generate_username(name):

    username = "".join(name.split(' ')).lower()
    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + str(random.randint(0, 1000))
        return generate_username(random_username)


def register_social_user(provider, user_id, email, name, first_name, last_name):
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():
        u = User.objects.get(email=email)
        token = u.password_string.encode()
        key = u.key.encode()
        f = Fernet(key)
        pass_word = f.decrypt(token).decode()

        if provider == filtered_user_by_email[0].auth_provider or filtered_user_by_email.exists():

            if filtered_user_by_email[0].is_active:
                registered_user = authenticate(
                    email=email, password=pass_word)

                return {
                    'username': registered_user.username,
                    'image': registered_user.image.url,
                    'email': registered_user.email,
                    'id': registered_user.id,
                    'is_user': registered_user.is_user,
                    'is_admin': registered_user.is_admin,
                    'is_staff': registered_user.is_staff,
                    'tokens': registered_user.tokens(),
                    'first_name': registered_user.first_name,
                    'updated': registered_user.updated,
                    }
            else:
                raise AuthenticationFailed(
                    detail='Account disabled, contact admin')

        else:
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

    else:
        password = str(random.randint(10000000, 90000000))
        key = Fernet.generate_key()
        f = Fernet(key)
        token = f.encrypt(password.encode())

        user = {
            'username': generate_username(name), 'email': email,
            'password': password}
        user = User.objects.create_user(**user)
        user.is_verified = True
        user.first_name = first_name
        user.last_name = last_name
        user.is_user = True
        user.auth_provider = provider
        user.password_string = token.decode()
        user.key = key.decode()
        user.save()
        Wallet.objects.create(user=user)

        new_user = authenticate(
            email=email, password=password)
        return {
            'email': new_user.email,
            'image': new_user.image.url,
            'username': new_user.username,
            'id': new_user.id,
            'is_user': new_user.is_user,
            'is_admin': new_user.is_admin,
            'tokens': new_user.tokens(),
            'first_name': new_user.first_name,
            'updated': new_user.updated,
            'is_staff': new_user.is_staff,
            "new": True
        }
