from django.contrib import admin
from .models import BloodRequest

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'blood_group', 'status', 'created_at')
    list_filter = ('status', 'blood_group')
