from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Part, UAV

class PartInline(admin.TabularInline):
    model = Part
    extra = 0
    fields = ('serial_number', 'type', 'uav_type', 'produced_by', 'is_used', 'production_date')
    readonly_fields = ('production_date',)
    can_delete = False
    show_change_link = True

@admin.register(Part)
class PartAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'uav_type', 'produced_by', 'production_date', 'get_status')
    list_filter = ('type', 'uav_type', 'is_used')
    search_fields = ('id', 'produced_by__user__username')
    readonly_fields = ('production_date',)
    date_hierarchy = 'production_date'
    list_per_page = 20
    actions = ['mark_as_used', 'mark_as_unused']

    def get_status(self, obj):
        if obj.is_used:
            return format_html(
                '<span class="status-badge status-in-use">Kullanımda</span>'
            )
        return format_html(
            '<span class="status-badge status-in-stock">Stokta</span>'
        )
    get_status.short_description = 'Durum'

    def mark_as_used(self, request, queryset):
        queryset.update(is_used=True)
    mark_as_used.short_description = "Seçili parçaları kullanıldı olarak işaretle"

    def mark_as_unused(self, request, queryset):
        queryset.update(is_used=False)
    mark_as_unused.short_description = "Seçili parçaları stokta olarak işaretle"

@admin.register(UAV)
class UAVAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'assembled_by', 'assembly_date', 'get_parts_info')
    list_filter = ('type', 'assembly_date')
    search_fields = ('id', 'assembled_by__user__username')
    readonly_fields = ('assembly_date', 'get_parts_detail')
    date_hierarchy = 'assembly_date'
    list_per_page = 15
    fieldsets = (
        ('UAV Bilgileri', {
            'fields': ('type', 'serial_number', 'assembled_by')
        }),
        ('Parçalar', {
            'fields': ('wing', 'body', 'tail', 'avionics')
        }),
        ('Montaj Bilgileri', {
            'fields': ('assembly_date', 'get_parts_detail')
        }),
    )

    def get_parts_info(self, obj):
        parts_html = '<table style="width:100%; border-collapse: collapse;">'
        parts_html += '<tr style="background-color: #f5f5f5;"><th style="padding:5px;">Parça Tipi</th><th>Parça ID</th></tr>'
        
        parts = {
            'Kanat': obj.wing,
            'Gövde': obj.body,
            'Kuyruk': obj.tail,
            'Aviyonik': obj.avionics
        }
        
        for part_type, part in parts.items():
            parts_html += f'<tr><td style="padding:5px;">{part_type}</td><td>{part.id if part else "Eksik"}</td></tr>'
        
        parts_html += '</table>'
        return format_html(parts_html)
    get_parts_info.short_description = 'Parça Bilgileri'

    def get_parts_detail(self, obj):
        if not obj:
            return "-"
        return format_html(
            """
            <table class="custom-table">
                <tr>
                    <th>Parça</th>
                    <th>Seri No</th>
                    <th>Üretici</th>
                </tr>
                <tr><td>Kanat</td><td>{}</td><td>{}</td></tr>
                <tr><td>Gövde</td><td>{}</td><td>{}</td></tr>
                <tr><td>Kuyruk</td><td>{}</td><td>{}</td></tr>
                <tr><td>Aviyonik</td><td>{}</td><td>{}</td></tr>
            </table>
            """,
            obj.wing.serial_number, obj.wing.produced_by,
            obj.body.serial_number, obj.body.produced_by,
            obj.tail.serial_number, obj.tail.produced_by,
            obj.avionics.serial_number, obj.avionics.produced_by
        )
    get_parts_detail.short_description = "Parça Detayları"

    def get_parts_summary(self, obj):
        return format_html(
            '<span class="status-badge info" title="{}">Tüm parçalar monte edildi</span>',
            f"Kanat: {obj.wing.serial_number}\n"
            f"Gövde: {obj.body.serial_number}\n"
            f"Kuyruk: {obj.tail.serial_number}\n"
            f"Aviyonik: {obj.avionics.serial_number}"
        )
    get_parts_summary.short_description = "Parça Durumu"
