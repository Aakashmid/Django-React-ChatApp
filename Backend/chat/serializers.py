from rest_framework import serializers
from .models import User, Conversation, ConversationParticipant, Message
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar', 'bio', 'is_online', 'first_name', 'last_name']
        read_only_fields = ['is_online']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['full_name'] = f"{instance.first_name} {instance.last_name}"
        return data


class ConversationParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ConversationParticipant
        fields = ['user', 'joined_at', 'last_read_at']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp', 'is_read']


class ConversationSerializer(serializers.ModelSerializer):
    participants = ConversationParticipantSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'name', 'type', 'created_at', 'last_message_at', 'participants', 'last_message']

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        return MessageSerializer(last_message).data if last_message else None


########## Auth related serializers  #########


########


########
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    # email = serializers.EmailField(
    #     validators=[UniqueValidator(queryset=User.objects.all())],
    #     required=True,
    #     error_messages={'required': 'Email is required', 'invalid': 'Enter a valid email address'},
    # )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user


########
class LoginSerializer(serializers.Serializer):
    email_or_username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):
        email_or_username = data.get('email_or_username')
        password = data.get('password')

        if '@' in email_or_username:
            user = authenticate(request=self.context.get('request'), username=email_or_username, password=password)
        else:
            user = authenticate(request=self.context.get('request'), username=email_or_username, password=password)
        if not user:
            raise serializers.ValidationError('Invalid credentials')

        data['user'] = user
        return data

    def create(self, validated_data):
        user = validated_data['user']
        return user


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("New passwords do not match")
        return data


# class ForgetPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField()

#     def validate_email(self, value):
#         if not User.objects.filter(email=value).exists():
#             raise serializers.ValidationError("No user is associated with this email address")
#         return value
