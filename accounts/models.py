from django.db import models
from django.contrib.auth.models import User
from encrypted_model_fields.fields import EncryptedCharField
import random
from django.utils import timezone
import string

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    encrypted_info = EncryptedCharField(max_length=100)

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = EncryptedCharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp_code}"
    
    @staticmethod
    def generate_otp(user):
        """Genera un OTP de 6 dígitos para el usuario dado y lo guarda en la base de datos."""
        OTP.objects.filter(user=user).delete() 
        otp_code = ''.join(random.choices(string.digits, k=6))
        otp_instance = OTP.objects.create(user=user,otp_code=otp_code)
        return otp_instance
    
    def is_valid(self):
        """Verifica si el OTP es válido (no ha expirado)."""
        expiration_time = self.created_at + timezone.timedelta(minutes=15)
        return timezone.now() < expiration_time