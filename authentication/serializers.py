from rest_framework import serializers
from .models import User, Chat, Traders
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from notifications.models import Notification
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils import timezone


class RelatedFieldAlternative(serializers.PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        self.serializer = kwargs.pop('serializer', None)
        if self.serializer is not None and not issubclass(self.serializer, serializers.Serializer):
            raise TypeError('"serializer" is not a valid serializer class')

        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        return False if self.serializer else True

    def to_representation(self, instance):
        if self.serializer:
            return self.serializer(instance, context=self.context).data
        return super().to_representation(instance)


class UserDetailsSerializer(serializers.ModelSerializer):
    # address = serializers.SerializerMethodField('_get_address')

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'image', 'mobile_no1', 'mobile_no2', 'address', 'country', 'state', 'gender',
            'thumbnail')

    # def _get_address(self, obj):
    #     setting = UserSettings.objects.get(user=obj)
    #     if setting.can_view_address:
    #         return {obj.address}


class AdminDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('country', 'state', 'mobile_no1', 'mobile_no2', 'address')


class StaffDetailsSerializer(serializers.ModelSerializer):
    # no_of_staffs = serializers.SerializerMethodField('get_staffs')

    class Meta:
        model = User
        fields = ('id', 'email', 'is_admin', 'is_staff', 'created_at', 'username', 'mobile_no', 'image', 'gender', 'first_name', 'last_name',
                  'is_verified', 'is_active')


class UserCrudSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'address', 'mobile_no1', 'mobile_no2', 'gender', 'country',
                  'state', 'about', 'bitcoin', 'instagram', 'twitter', 'otp')


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'address', 'mobile_no1', 'mobile_no2', 'gender', 'country',
                  'state', 'about', 'bitcoin', 'email', 'instagram', 'twitter', 'image', 'username',
                  'verified', 'applied')


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('image',)


class UserImageIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('imageId',)


class UserPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email',)


class RegisterStaffSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    default_error_messages = {
        'username': 'The username should only contain alphanumeric characters'}

    class Meta:
        model = User
        fields = ('email', 'password', 'mobile_no', 'first_name', 'last_name', 'gender')


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    default_error_messages = {
        'username': 'The username should only contain alphanumeric characters'}

    class Meta:
        model = User
        fields = ['email', 'password', 'refereeCodeLiteral']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    refereeCodeLiteral = serializers.CharField(
        max_length=68, min_length=6, write_only=True)

    default_error_messages = {
        'username': 'The username should only contain alphanumeric characters'}

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        # username = attrs.get('username', '')

        # if not username.isalnum():
        #     raise serializers.ValidationError(
        #         self.default_error_messages)
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(
        max_length=255, min_length=3, read_only=True)
    mobile_no = serializers.CharField(read_only=True)

    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(email=obj['email'])

        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access'],
        }

    class Meta:
        model = User
        fields = ['email', 'password', 'username', 'tokens', 'is_admin', 'is_staff', 'is_user', 'id',
                  'image', 'mobile_no', 'updated', 'first_name']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        filtered_user_by_email = User.objects.filter(email=email)
        user = auth.authenticate(email=email, password=password)
        activeUser = User.objects.filter(email=email)

        if filtered_user_by_email.exists() and filtered_user_by_email[0].auth_provider != 'email':
            raise AuthenticationFailed(
                {'detail': 'Please continue your sign in with ' + filtered_user_by_email[
                    0].auth_provider + ' or reset your password and be able to sign in either '
                                       'through google or by using your email and new password',
                 'error': "email is google"})
        # if user.is_school_staff and not user.school.subscribed:
        #     raise AuthenticationFailed("You don't have an active subscription, subscribe to continue")
        if not activeUser[0].is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')
        if user.is_admin or user.is_staff:
            return {
                'email': user.email,
                'image': user.thumbnail,
                'username': user.username,
                'is_admin': user.is_admin,
                'is_user': user.is_user,
                'is_staff': user.is_staff,
                'tokens': user.tokens,
                'id': user.id,
                'mobile_no': user.mobile_no,
                'updated': user.updated,
                'first_name': user.first_name
            }
        else:
            return {
                'email': user.email,
                'image': user.image,
                'username': user.username,
                'is_admin': user.is_admin,
                'is_user': user.is_user,
                'is_staff': user.is_staff,
                'tokens': user.tokens,
                'id': user.id,
                'mobile_no': user.mobile_no,
                'updated': user.updated,
                'first_name': user.first_name
            }

        return super().validate(attrs)


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(min_length=2)

    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']


class PassSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password']


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {
        'bad_token': 'Token has expired or is invalid'
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):

        try:
            token = RefreshToken(self.token)
            token.blacklist()

        except TokenError:
            self.fail('bad_token')


class NotificationsSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('_get_related')

    class Meta:
        model = Notification
        fields = '__all__'
        depth = 0

    def _get_related(self, obj):
        serializer = User.objects.get(id=int(obj.actor_object_id))
        return serializer.username


class ChatSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('_get_related')
    image = serializers.SerializerMethodField('get_image')
    location = serializers.SerializerMethodField('get_location')

    class Meta:
        model = Chat
        fields = '__all__'

    def _get_related(self, obj):
        return obj.user.username

    def get_image(self, obj):
        return obj.user.image.url

    def get_location(self, obj):
        return obj.user.country


class AddChatSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=200)


class GetUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'verified', 'date_joined', 'image', 'country', 'gender', 'first_name', 'last_name',
                  'mobile_no1', 'mobile_no2', 'state', 'twitter', 'instagram', 'thumbnail', 'email', 'applied',
                  'profit_percentage')


class AddTraderSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)