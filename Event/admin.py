from django.contrib import admin
from .models import Event

# Register your models here.

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'start_time', 'end_time', 'created_by')
    list_filter = ('category', 'start_time')
    search_fields = ('title', 'location', 'description')