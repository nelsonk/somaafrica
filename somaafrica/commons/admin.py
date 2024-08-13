# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# from .forms import UserCreationForm, UserChangeForm
# from .models import User


# class UserAdmin(BaseUserAdmin):
#     form = UserChangeForm
#     add_form = UserCreationForm

#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Personal info', {'fields': ('email',)}),
#         ('Permissions', {
#             'fields': (
#                 'is_active',
#                 'is_staff',
#                 'is_superuser',
#                 'groups',
#                 'user_permissions'
#             )
#         }),
#         ('Important dates', {
#             'fields': ('last_login', 'created_at', 'updated_at')
#         }),
#     )
#     readonly_fields = ('created_at', 'updated_at')

#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'email', 'password1', 'password2'),
#         }),
#     )
#     list_display = ('username', 'email', 'is_staff', 'is_active')
#     search_fields = ('username', 'email')
#     ordering = ('username',)


# admin.site.register(User, UserAdmin)
