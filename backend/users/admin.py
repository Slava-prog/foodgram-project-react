from django.contrib import admin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'username',
                    'email',
                    'role',
                    'first_name',
                    'last_name',
                    'is_subscribed',
                    'password'
                    )
    list_filter = ('email', 'username')
