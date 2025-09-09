from django.contrib import admin
from.models import Profile,Batch


# Register your models here.
admin.site.register(Profile)

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_dispaly=('name','description','required_events')
    search_fields=('name',)
    


