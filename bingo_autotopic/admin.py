from django.contrib import admin
from models import *


class GameDescriptionAdmin(admin.ModelAdmin):
    list_display = ("description", "start_time", "end_time", "site")
    list_filter = ("site",)


admin.site.register(GameDescription, GameDescriptionAdmin)
