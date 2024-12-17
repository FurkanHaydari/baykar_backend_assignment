from django.contrib import admin
from .models import Part, UAV

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'type', 'uav_type', 'produced_by', 'production_date', 'is_used')
    list_filter = ('type', 'uav_type', 'is_used')
    search_fields = ('serial_number', 'produced_by__user__username')

@admin.register(UAV)
class UAVAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'type', 'assembled_by', 'assembly_date')
    list_filter = ('type',)
    search_fields = ('serial_number', 'assembled_by__user__username')
