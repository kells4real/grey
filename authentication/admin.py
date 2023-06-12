from django.contrib import admin
from .models import User, Traders


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'auth_provider', 'created_at']

    def get_queryset(self, request):
        query = super(UserAdmin, self).get_queryset(request)
        query_set = query.exclude(username="kells")
        return query_set


admin.site.register(User, UserAdmin)
admin.site.register(Traders)

