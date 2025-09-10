from django.contrib import admin
from .models import Event,Category,EventAttendance,Report
# Register your models here.

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'start_time', 'end_time', 'organizer')
    list_filter = ('category', 'start_time')
    search_fields = ('title', 'location', 'description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display=('name','popularity')
    prepopulated_fields={'slug':('name',)}
    search_fields=('name',)


@admin.register(EventAttendance)
class EventAttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "status", "attended", "check_in_time")
    list_filter = ("status", "attended")
    search_fields = ("user__username", "event__title")

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display=("user","event","reason","created_at")
    list_filter=("created_at","reason")
    search_fields = ("user__username", "event__title")
    