from django.contrib import admin
from .models import Student, Instructor, Course, Enrollment, Feedback, UserProfile

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'faculty', 'is_active']
    list_filter = ['is_active', 'faculty', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']
    list_editable = ['is_active']
    ordering = ['last_name', 'first_name']
    fieldsets = (
        ('Основная информация', {
            'fields': ('first_name', 'last_name', 'email', 'birth_date')
        }),
        ('Университет', {
            'fields': ('faculty', 'is_active')
        }),
    )

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'specialization', 'is_active']
    list_filter = ['is_active', 'specialization']
    search_fields = ['first_name', 'last_name', 'email']
    ordering = ['last_name', 'first_name']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'duration', 'level', 'price', 'is_active']
    list_filter = ['is_active', 'level', 'instructor']
    search_fields = ['title', 'description']
    list_editable = ['is_active', 'price']
    ordering = ['title']
    # Автозаполнение slug на основе title
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'description')
        }),
        ('Детали курса', {
            'fields': ('duration', 'instructor', 'level', 'max_students', 'price')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
    )

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrollment_date', 'status']
    list_filter = ['status', 'enrollment_date', 'course']
    search_fields = ['student__first_name', 'student__last_name', 'course__title']
    date_hierarchy = 'enrollment_date'

# Тут регистрируем существующие модели
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'subject']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'created_at']
    search_fields = ['username', 'email']