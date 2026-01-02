from django.contrib import admin
from user_auth_app.models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'type']

    def username(self, obj):
        return obj.user.username
    
    def email(self, obj):
        return obj.user.email