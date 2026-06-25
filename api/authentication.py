import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.hashers import is_password_usable
from rest_framework import authentication, exceptions
# pyrefly: ignore [missing-import]
from .models import User


def verify_user_password(user, password):
    """Verify password and auto-rehash legacy plain-text passwords."""
    if user.check_password(password):
        return True

    stored = user.password or ''
    if stored and not is_password_usable(stored) and stored == password:
        user.set_password(password)
        user.save(update_fields=['password'])
        return True

    return False


def build_auth_response(user, request):
    """Consistent login/register token payload for the web client."""
    token = generate_jwt(user)
    from .serializers import UserSerializer

    return {
        'success': True,
        'access': token,
        'refresh': token,
        'token': token,
        'user': UserSerializer(user, context={'request': request}).data,
    }


def generate_jwt(user):
    """Generate JWT token for user"""
    payload = {
        'user_id': str(user.id),
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(days=settings.JWT_EXPIRATION_DAYS),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token


def decode_jwt(token):
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed('Token telah kadaluarsa')
    except jwt.InvalidTokenError:
        raise exceptions.AuthenticationFailed('Token tidak valid')
    except Exception:
        raise exceptions.AuthenticationFailed('Gagal memproses token')


class JWTAuthentication(authentication.BaseAuthentication):
    """Custom JWT Authentication"""

    def authenticate_header(self, request):
        return 'Bearer'

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        try:
            parts = auth_header.split(' ')
            if len(parts) != 2:
                return None
            prefix, token = parts
            if prefix.lower() != 'bearer':
                return None
        except ValueError:
            raise exceptions.AuthenticationFailed('Format header Authorization tidak valid')

        payload = decode_jwt(token)
        user_id = payload.get('user_id')
        
        if not user_id:
            raise exceptions.AuthenticationFailed('Payload token tidak lengkap')

        try:
            from django.core.exceptions import ValidationError
            user = User.objects.get(id=user_id)
        except (User.DoesNotExist, ValidationError, ValueError):
            raise exceptions.AuthenticationFailed('User tidak ditemukan atau ID tidak valid')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User tidak aktif')

        return (user, token)
