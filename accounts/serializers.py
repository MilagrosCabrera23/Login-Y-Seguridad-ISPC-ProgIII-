from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from .models import OTP

class UserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo User."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer para registrar un nuevo usuario, incluye el campo de contraseña."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para el modelo UserProfile, incluye el campo de usuario anidado."""
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ['user', 'encrypted_info']

class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer para solicitar el restablecimiento de contraseña."""
    email = serializers.EmailField()

    def validate_email(self, value):
        """Valida que el correo electrónico exista en el sistema."""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No existe un usuario con este correo electrónico.")
        return value
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer para confirmar el restablecimiento de contraseña con OTP."""
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
       """Valida que el OTP sea correcto para el correo electrónico proporcionado."""
       try:
           user = User.objects.get(email=data['email'])
           otp = OTP.objects.get(user=user, otp_code=data['otp_code'])

       except(User.DoesNotExist, OTP.DoesNotExist):
            raise serializers.ValidationError("OTP inválido o correo electrónico no encontrado.")
       
       if not otp.is_valid():
           raise serializers.ValidationError("El OTP ha expirado o ya ha sido utilizado.") 
       
       self.context['user'] = user
       return data