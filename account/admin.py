from django.contrib import admin

from .models import UserTaskToken

# Register your models here.
@admin.register(UserTaskToken)
class UserTaskTokenAdmin(admin.ModelAdmin):
    model = UserTaskToken

    list_display = (
        "task",
        "state",
        "user",
        "token",
        "expires_at",
    )

    list_filter = (
        "task",
        "state",
    )

    list_editable = ()

    search_fields = (
        "user",
    )

    fields = (
        "token",
        "task",
        "state",
        "user",
    )

    readonly_fields = [
        "token",
        "task",
        # "state",
        "user",
    ]

    save_on_top = True
