from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import StudentProfile, Achievement, ContactMessage

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile'
    fields = ('roll_number', 'department', 'year', 'phone', 'avatar', 'bio')
    readonly_fields = ('created_at', 'updated_at')

class CustomUserAdmin(UserAdmin):
    inlines = (StudentProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_roll_number', 'get_department', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'studentprofile__year', 'studentprofile__department')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'studentprofile__roll_number')
    ordering = ('-date_joined',)
    
    def get_roll_number(self, obj):
        return obj.studentprofile.roll_number if hasattr(obj, 'studentprofile') else 'N/A'
    get_roll_number.short_description = 'Roll Number'
    get_roll_number.admin_order_field = 'studentprofile__roll_number'
    
    def get_department(self, obj):
        return obj.studentprofile.department if hasattr(obj, 'studentprofile') else 'N/A'
    get_department.short_description = 'Department'
    get_department.admin_order_field = 'studentprofile__department'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_name', 'student_roll_number', 'event', 'prize', 'competition_level', 'is_approved', 'date_achieved', 'created_at')
    list_filter = ('is_approved', 'competition', 'date_achieved', 'created_at')
    search_fields = ('name', 'event', 'student__username', 'student__first_name', 'student__last_name', 'student__studentprofile__roll_number')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    actions = ['approve_achievements', 'disapprove_achievements']
    
    def student_name(self, obj):
        return obj.student_name
    student_name.short_description = 'Student Name'
    student_name.admin_order_field = 'student__first_name'
    
    def student_roll_number(self, obj):
        return obj.student_roll_number
    student_roll_number.short_description = 'Roll Number'
    student_roll_number.admin_order_field = 'student__studentprofile__roll_number'
    
    def competition_level(self, obj):
        return obj.competition_level_display
    competition_level.short_description = 'Competition Level'
    
    def approve_achievements(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} achievements approved successfully.')
    approve_achievements.short_description = "Approve selected achievements"
    
    def disapprove_achievements(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} achievements disapproved.')
    disapprove_achievements.short_description = "Disapprove selected achievements"

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    list_editable = ('is_read',)
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} messages marked as read.')
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} messages marked as unread.')
    mark_as_unread.short_description = "Mark selected messages as unread"
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        if obj:
            return True
        return super().has_change_permission(request, obj)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Custom admin site header and title
admin.site.site_header = "CSE Achievers Portal Administration"
admin.site.site_title = "CSE Achievers Portal Admin"
admin.site.index_title = "Welcome to CSE Achievers Portal Administration"