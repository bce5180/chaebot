from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, KakaoUser, NaverUser, FileUpload


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("user_id", "age_group", "gender")}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(KakaoUser)
admin.site.register(NaverUser)
admin.site.register(FileUpload)
