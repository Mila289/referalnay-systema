from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import UserService
from .models import User


class AuthView(APIView):
    async def post(self, request):
        phone_number = request.data.get('phone')
        if not phone_number:
            return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = await UserService.authenticate(phone_number)
        return Response({"message": "Authentication successful", "user_id": user.id, "invite_code": user.invite_code})


class VerifyCodeView(APIView):
    async def post(self, request):
        phone_number = request.data.get('phone')
        code = request.data.get('auth_code')

        try:
            user = await User.objects.get(phone_number=phone_number)
            await UserService.verify_auth_code(user, code)
            return Response({"message": "Code verified successfully"})
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class ProfileView(APIView):
    async def get(self, request):
        phone_number = request.query_params.get('phone')
        try:
            user = await User.objects.get(phone_number=phone_number)
            profile = UserService.get_user_profile(user)
            return Response(profile)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class ActivateInviteView(APIView):
    async def post(self, request):
        phone_number = request.data.get('phone')
        code = request.data.get('code')

        try:
            user = await User.objects.get(phone_number=phone_number)
            await UserService.activate_invite_code(user, code)
            return Response({"message": "Invite code activated successfully"})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
