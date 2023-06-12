import datetime

from django.db import models
from PIL import Image
from django.utils.text import slugify
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.conf import settings
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from io import BytesIO
from django.core.files import File
# from django.core.files.storage import default_storage as storage
# import io
# from io import BytesIO
# from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from django.core.files.base import ContentFile
import os
from django.core.files.uploadedfile import InMemoryUploadedFile
import random
from django.core.validators import MaxValueValidator, MinValueValidator


def getCode():
    a = random.randint(0, 9)
    b = random.randint(0, 9)
    c = random.randint(0, 9)
    d = random.randint(0, 9)
    e = random.randint(0, 9)
    return f"{a}{b}{c}{d}{e}"


def make_thumbnail(dst_image_field, src_image_field, size, name_suffix, sep='_'):
    """
    make thumbnail image and field from source image field

    @example
        thumbnail(self.thumbnail, self.image, (200, 200), 'thumb')
    """
    # create thumbnail image
    image = Image.open(src_image_field)
    image.thumbnail(size, Image.ANTIALIAS)

    # build file name for dst
    dst_path, dst_ext = os.path.splitext(os.path.basename(src_image_field.name))
    dst_ext = dst_ext.lower()
    dst_fname = '{}{}'.format(dst_path, dst_ext)

    # check extension
    if dst_ext in ['.jpg', '.jpeg']:
        filetype = 'JPEG'
    elif dst_ext == '.gif':
        filetype = 'GIF'
    elif dst_ext == '.png':
        filetype = 'PNG'
    else:
        raise RuntimeError('unrecognized file type of "%s"' % dst_ext)

    # Save thumbnail to in-memory file as StringIO
    dst_bytes = BytesIO()
    image.save(dst_bytes, filetype)
    dst_bytes.seek(0)

    # set save=False, otherwise it will run in an infinite loop
    dst_image_field.save(dst_fname, ContentFile(dst_bytes.read()), save=False)
    dst_bytes.close()


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('Users should have a username')
        if email is None:
            raise TypeError('Users should have a Email')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None):
        if password is None:
            raise TypeError('Password should not be none')

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google',
                  'twitter': 'twitter', 'email': 'email'}


def user_image_upload(instance, filename):
    title = instance.username
    slug = slugify(title)
    return f"user_images/{slug}/{filename}"


def default_user_image(instance):
    gender = instance.gender
    if gender == "Male":
        return "man.jpg"
    else:
        return "woman.png"


# All user types on a single model distinguished by boolean fields
class User(AbstractBaseUser, PermissionsMixin):
    choices = (
        ("Male", "Male"),
        ("Female", "Female")
    )
    username = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_user = models.BooleanField(default=False)
    updated = models.BooleanField(default=False)
    mobile_no = models.CharField(max_length=20, null=True, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    password_string = models.CharField(null=True, max_length=500, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=user_image_upload, null=True, blank=True)
    imageId = models.ImageField(upload_to=user_image_upload, null=True, blank=True)
    about = models.TextField(max_length=800, null=True, blank=True)
    facebook = models.CharField(null=True, blank=True, max_length=100)
    twitter = models.CharField(null=True, blank=True, max_length=100)
    instagram = models.CharField(null=True, blank=True, max_length=100)
    thumbnail = models.ImageField(upload_to=user_image_upload, null=True, blank=True)
    violation = models.IntegerField(default=0)
    gender = models.CharField(max_length=100, choices=choices, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    mobile_no1 = models.CharField(max_length=100, null=True, blank=True)
    mobile_no2 = models.CharField(max_length=100, null=True, blank=True)
    email_token = models.TextField(null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=400, null=True, blank=True)
    key = models.TextField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True)
    referenceCode = models.CharField(max_length=10, unique=True)
    referee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, null=True, blank=True)
    signal_strength = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    otp = models.IntegerField(default=0)
    referred = models.BooleanField(default=False)
    bitcoin = models.CharField(max_length=200, null=True, blank=True)
    refereeCodeLiteral = models.CharField(max_length=50, blank=True, null=True)
    applied = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    profit_percentage = models.IntegerField(default=0)
    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('email'))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    # Automatically get a unique username
    def _get_unique_username(self):
        email = str(self.email)
        user_strng = email.split('@')[0]
        unique_username = user_strng
        num = 1
        while User.objects.filter(username=unique_username).exists():
            unique_username = '{}{}'.format(user_strng, num)
            num += 1
        return unique_username

    # Automatically generate a unique reference code on the fly
    def _get_unique_refCode(self):
        code = getCode()
        unique_code = code
        num = 1
        while User.objects.filter(referenceCode=code).exists():
            unique_code = int(code) + num
            num += 1
        return str(unique_code)

    # Custom save function
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self._get_unique_username()

        if not self.referenceCode:
            self.referenceCode = self._get_unique_refCode()

        if not self.image and not self.id:
            if self.gender == "Female":
                self.image = "girl.jpeg"
                self.thumbnail = "girl.jpeg"
            else:
                self.image = 'boy.jpg'
                self.thumbnail = 'boy.jpg'

            # make_thumbnail(self.image, self.image, (500, 750), 'thumb')
            # make_thumbnail(self.thumbnail, self.image, (100, 100), 'icon')
        super(User, self).save()

        img = Image.open(self.image.path)

        output_size = (150, 150)
        img.thumbnail(output_size)
        img.save(self.image.path)


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=200)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class Traders(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    traders = models.ManyToManyField(User, blank=True, related_name="all_traders")

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "Traders"
