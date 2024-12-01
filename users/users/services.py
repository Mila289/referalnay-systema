from .models import User
import asyncio

class UserService:
    @staticmethod
    async def authenticate(phone_number):
        user, _ = User.objects.get_or_create(phone_number=phone_number)
        await asyncio.sleep(1)  # Имитация задержки в 1 сек
        if user.invite_code == '':
            user.invite_code = user.generate_invite_code()
            user.save()
        return user

    @staticmethod
    async def verify_auth_code(user, code):
        if user.auth_code == code:
            return user
        raise ValueError("Invalid auth code")

    @staticmethod
    async def activate_invite_code(user, code):
        if User.objects.filter(invite_code=code).exists():
            user.activated_invite_code = code
            user.save()
            return user
        raise ValueError("Invalid invite code")

    @staticmethod
    def get_user_profile(user):
        return {
            "phone": user.phone_number,
            "invite_code": user.invite_code,
            "activated_invite_code": user.activated_invite_code,
            "used_by": User.objects.filter(activated_invite_code=user.invite_code).values_list('phone_number', flat=True)
        }
