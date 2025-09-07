from django.contrib import admin
from .models import Event,Category
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

