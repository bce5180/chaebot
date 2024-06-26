# myapp/kakaoSave.py

from allauth.socialaccount.signals import social_account_updated, social_account_added
from django.dispatch import receiver
from .models import KakaoUser
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount
import logging

logger = logging.getLogger(__name__)


@receiver(social_account_added)
@receiver(social_account_updated)
def populate_profile(request, sociallogin, **kwargs):
    user = sociallogin.user
    extra_data = sociallogin.account.extra_data
    logger.debug(f"Kakao extra_data: {extra_data}")

    nickname = extra_data.get("properties", {}).get("nickname", user.username)
    email = extra_data.get("kakao_account", {}).get("email", "")
    gender = extra_data.get("kakao_account", {}).get("gender", "")
    age_range = extra_data.get("kakao_account", {}).get("age_range", "")

    KakaoUser.objects.update_or_create(
        user=user,
        defaults={
            "nickname": nickname,
            "email": email,
            "gender": gender,
            "age_range": age_range,
        },
    )
