from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Register a new user (talent or client)."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Login with username and password, returns JWT tokens."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if not user:
            return Response(
                {'detail': 'Credenciales inválidas.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class MeView(generics.RetrieveUpdateAPIView):
    """Get or update the authenticated user's profile."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class PasswordResetRequestView(APIView):
    """Request a password reset. Sends email with reset link."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal whether email exists
            return Response({
                'message': 'Si el email existe, recibirás instrucciones para restablecer tu contraseña.'
            })

        # Generate token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Send email
        from .emails import send_password_reset_email
        send_password_reset_email(user, uid, token)

        # Build response
        reset_url = f"/reset-password?uid={uid}&token={token}"
        response_data = {
            'message': 'Si el email existe, recibirás instrucciones para restablecer tu contraseña.',
        }

        # Dev mode: include direct link (remove in production)
        from django.conf import settings
        if settings.DEBUG:
            response_data['reset_url'] = reset_url
            response_data['uid'] = uid
            response_data['token'] = token

        return Response(response_data)


class PasswordResetConfirmView(APIView):
    """Confirm password reset with uid and token."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = request.data.get('uid')
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']

        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'detail': 'Enlace de restablecimiento inválido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {'detail': 'El enlace ha expirado o es inválido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Contraseña restablecida exitosamente.'})
