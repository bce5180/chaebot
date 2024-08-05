from django.apps import AppConfig

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        pass
        # import myapp.userSave  # 주석 처리하여 임포트를 일시적으로 비활성화
