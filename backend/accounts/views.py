from rest_framework import generics, permissions, status, parsers
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

        # Welcome email (fail-silently — no rompe registro si SMTP falla)
        try:
            from .emails import send_welcome_email
            send_welcome_email(user)
        except Exception:
            pass

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


VALID_PARTNER_OFFERS = {'referral', 'packs', 'venue'}


class PartnerRoleToggleView(APIView):
    """
    Activa o desactiva el rol Aliado para el usuario autenticado.

    POST body:
      { "active": true/false, "offers": ["referral", ...] }

    Reglas:
      - El rol primario sigue siendo `role` (cliente/talento/admin) — no se toca.
      - Admin NO puede activarse como partner (separación de poderes).
      - Si `active=false` se limpia partner_offers.
      - Si `active=true` y offers vacío, se asume ['referral'] por defecto (v1).
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.role == 'admin':
            return Response(
                {'detail': 'Los administradores no pueden activarse como Aliado.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        active = bool(request.data.get('active', False))
        offers = request.data.get('offers')
        if offers is None:
            offers = ['referral'] if active else []

        if not isinstance(offers, list):
            return Response(
                {'detail': '`offers` debe ser una lista.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invalid = [o for o in offers if o not in VALID_PARTNER_OFFERS]
        if invalid:
            return Response(
                {'detail': f'Ofertas inválidas: {invalid}. Permitidas: {sorted(VALID_PARTNER_OFFERS)}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if active and not offers:
            return Response(
                {'detail': 'Activá al menos una sub-oferta del rol Aliado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_partner_active = active
        user.partner_offers = offers if active else []
        user.save(update_fields=['is_partner_active', 'partner_offers', 'updated_at'])

        return Response(UserSerializer(user).data)


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


class AvatarUploadView(APIView):
    """Upload or update the authenticated user's avatar."""
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request):
        avatar = request.FILES.get('avatar')
        if not avatar:
            return Response(
                {'error': 'No se proporcionó ninguna imagen.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        allowed = ['image/jpeg', 'image/png', 'image/webp']
        if avatar.content_type not in allowed:
            return Response(
                {'error': 'Solo se permiten imágenes JPG, PNG o WebP.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = request.user
        # Delete old avatar if exists
        if user.avatar:
            user.avatar.delete(save=False)

        user.avatar = avatar
        user.save(update_fields=['avatar'])

        return Response({
            'message': 'Avatar actualizado.',
            'avatar': user.avatar.url,
        })


class DeleteAccountView(APIView):
    """Soft-delete (anonimiza) la cuenta del usuario autenticado."""
    permission_classes = [permissions.IsAuthenticated]

    ACTIVE_BOOKING_STATUSES = [
        'solicitud_enviada', 'pendiente_respuesta', 'aceptada',
        'pendiente_pago', 'confirmada', 'en_disputa',
    ]

    def post(self, request):
        user = request.user
        confirm = (request.data.get('confirm_email') or '').strip().lower()
        if not confirm or confirm != (user.email or '').strip().lower():
            return Response(
                {'error': 'Debes escribir tu email exactamente para confirmar.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Bloquear si hay reservas activas (proteger a la contraparte)
        from bookings.models import Booking
        active_q = Booking.objects.filter(status__in=self.ACTIVE_BOOKING_STATUSES)
        if user.role == 'talent':
            from talents.models import TalentProfile
            try:
                profile = TalentProfile.objects.get(user=user)
                if active_q.filter(talent=profile).exists():
                    return Response(
                        {'error': 'Tienes reservas activas. Termínalas o cancélalas antes de eliminar la cuenta.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except TalentProfile.DoesNotExist:
                pass
        elif user.role == 'partner':
            if active_q.filter(partner=user).exists():
                return Response(
                    {'error': 'Tienes reservas activas gestionadas. Termínalas antes de eliminar la cuenta.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            if active_q.filter(client=user).exists():
                return Response(
                    {'error': 'Tienes reservas activas. Termínalas o cancélalas antes de eliminar la cuenta.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Anonimizar
        uid = user.pk
        if user.avatar:
            try:
                user.avatar.delete(save=False)
            except Exception:
                pass
        user.email = f'deleted_{uid}@deleted.pulsar'
        user.username = f'deleted_{uid}'
        user.first_name = ''
        user.last_name = ''
        user.phone = ''
        user.city = ''
        user.bio = ''
        user.is_active = False
        user.set_unusable_password()
        user.save()

        # Si es talent, ocultar el perfil para que no salga en búsqueda
        if user.role == 'talent':
            from talents.models import TalentProfile
            TalentProfile.objects.filter(user=user).update(
                is_approved=False, is_available=False
            )

        return Response({'message': 'Cuenta eliminada. Gracias por usar Pulsar.'})


class GoogleAuthView(APIView):
    """Authenticate with Google ID token. Creates account if new user."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('credential')
        role = request.data.get('role', 'client')

        if not token:
            return Response(
                {'error': 'Token de Google requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify Google token
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        from django.conf import settings

        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
        except ValueError:
            return Response(
                {'error': 'Token de Google inválido.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        email = idinfo.get('email')
        if not email:
            return Response(
                {'error': 'No se pudo obtener el email de Google.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')
        picture = idinfo.get('picture', '')

        # Find or create user
        is_new = False
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create new user
            username = email.split('@')[0]
            # Ensure unique username
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role if role in ['client', 'talent', 'partner'] else 'client',
                is_verified=True,
            )
            is_new = True
            # Welcome email para nuevos usuarios via Google
            try:
                from .emails import send_welcome_email
                send_welcome_email(user)
            except Exception:
                pass

        # Download Google avatar if user has no avatar
        if not user.avatar and picture:
            try:
                import urllib.request
                from django.core.files.base import ContentFile
                img_data = urllib.request.urlopen(picture).read()
                user.avatar.save(f'google_{user.pk}.jpg', ContentFile(img_data), save=True)
            except Exception:
                pass  # Non-critical, skip if fails

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'is_new': is_new,
        }, status=status.HTTP_200_OK)
