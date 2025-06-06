from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, CrimeReport

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'dob', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'dob')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}), 
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'dob', 'password1', 'password2'),
        }),
    )    

admin.site.register(UserProfile, CustomUserAdmin)

from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'created_at')
    search_fields = ('title', 'message')
    list_filter = ('notification_type', 'created_at')

from django.contrib import admin
from .models import CrimeReport

class CrimeReportAdmin(admin.ModelAdmin):
    list_display = ('type_of_crime', 'location_of_crime', 'date_of_crime', 'is_approved')
    list_filter = ('is_approved', 'type_of_crime', 'date_of_crime')
    actions = ['approve_crimes']

    def approve_crimes(self, request, queryset):
        queryset.update(is_approved=True)

    approve_crimes.description = "Mark selected crimes as approved"

admin.site.register(CrimeReport,CrimeReportAdmin)