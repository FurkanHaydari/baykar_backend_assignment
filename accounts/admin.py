from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Team, TeamMember

class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1
    fields = ('user', 'join_date')
    readonly_fields = ('join_date',)
    autocomplete_fields = ['user']
    show_change_link = True

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'member_count', 'get_members_list')
    search_fields = ('name', 'description')
    inlines = [TeamMemberInline]
    list_per_page = 20

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            member_count=Count('members')
        )

    def member_count(self, obj):
        return obj.member_count
    member_count.admin_order_field = 'member_count'
    member_count.short_description = 'Üye Sayısı'

    def get_members_list(self, obj):
        members = obj.members.select_related('user').all()[:5]
        member_list = [
            f'<span class="status-badge info">{member.user.username}</span>'
            for member in members
        ]
        total = obj.members.count()
        
        if total > 5:
            member_list.append(
                f'<span class="status-badge warning">ve {total-5} kişi daha...</span>'
            )
            
        return format_html(" ".join(member_list))
    get_members_list.short_description = 'Takım Üyeleri'

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'join_date', 'get_user_email')
    list_filter = ('team', 'join_date')
    search_fields = ('user__username', 'user__email', 'team__name')
    date_hierarchy = 'join_date'
    raw_id_fields = ('user',)
    list_per_page = 25
    autocomplete_fields = ['team']

    def get_user_email(self, obj):
        return format_html('<a href="mailto:{0}">{0}</a>', obj.user.email)
    get_user_email.short_description = 'E-posta'
    get_user_email.admin_order_field = 'user__email'
