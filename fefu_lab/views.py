from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import FeedbackForm, RegistrationForm, LoginForm
from .models import UserProfile, Feedback, Student, Course, Instructor, Enrollment
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    ProfileUpdateForm,
    PasswordChangeCustomForm
)

def home_page(request):
    # Статистика для главной страницы
    total_students = Student.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_instructors = Instructor.objects.filter(is_active=True).count()
    # Последние добавленные курсы
    recent_courses = Course.objects.filter(is_active=True).order_by('-created_at')[:3]
    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_instructors': total_instructors,
        'recent_courses': recent_courses,
    }
    return render(request, 'fefu_lab/home.html', context)

def about_page(request):
    return render(request, 'fefu_lab/about.html')

def student_profile(request, student_id):
    try:
        student = Student.objects.get(id=student_id, is_active=True)
        enrollments = student.enrollments.filter(status='ACTIVE').select_related('course')
        context = {
            'student': student,
            'enrollments': enrollments,
            'student_id': student.id,
            'student_name': student.full_name,
            'faculty': student.get_faculty_display_name(),
            'status': 'Активен' if student.is_active else 'Неактивен',
        }
        return render(request, 'fefu_lab/student_profile.html', context)
    except Student.DoesNotExist:
        raise Http404("Студент не найден")

def student_profile_context(request):
    #Добавляет student_profile в контекст если пользователь авторизован
    if request.user.is_authenticated:
        try:
            return {'student_profile': request.user.student_profile}
        except:
            return {}
    return {}

class CourseView(View):
    def get(self, request, course_slug):
        try:
            course = Course.objects.get(slug=course_slug, is_active=True)
            enrollments_count = course.enrollments.filter(status='ACTIVE').count()
            available_spots = course.max_students - enrollments_count
            context = {
                'course': course,
                'course_slug': course.slug,
                'enrollments_count': enrollments_count,
                'available_spots': available_spots,
                'title': course.title,
                'description': course.description,
                'duration': course.duration,
                'instructor': course.instructor.full_name if course.instructor else 'Не назначен',
                'level': course.get_level_display(),
                'price': course.price,
            }
            return render(request, 'fefu_lab/course_detail.html', context)
        except Course.DoesNotExist:
            raise Http404("Курс не найден")

def register_view(request):
    #Регистрация нового пользователя
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаем профиль студента
            student_profile = Student.objects.get(user=user)
            student_profile.first_name = form.cleaned_data['first_name']
            student_profile.last_name = form.cleaned_data['last_name']
            student_profile.email = form.cleaned_data['email']
            student_profile.save()
            # Автоматически входим после регистрации
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'fefu_lab/registration/register.html', {
        'form': form,
        'title': 'Регистрация'
    })

def login_view(request):
    #Вход в систему
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.first_name}!')
            # Перенаправляем на страницу, с которой пришли, или на профиль
            next_url = request.GET.get('next', 'profile')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверный email или пароль')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'fefu_lab/registration/login.html', {
        'form': form,
        'title': 'Вход в систему'
    })

def logout_view(request):
    #Выход из системы
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы')
    return redirect('home')

@login_required
def profile_view(request):
    #Личный кабинет пользователя
    try:
        student_profile = request.user.student_profile
    except Student.DoesNotExist:
        # Если профиль не существует, создаем его
        student_profile = Student.objects.create(
            user=request.user,
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            email=request.user.email,
            role='STUDENT'
        )
    # Получаем активные записи на курсы для студентов
    enrollments = None
    if student_profile.role == 'STUDENT':
        enrollments = student_profile.enrollments.filter(status='ACTIVE').select_related('course')
    # Получаем курсы преподавателя
    teacher_courses = None
    if student_profile.role == 'TEACHER':
        teacher_courses = student_profile.courses.all()
    return render(request, 'fefu_lab/registration/profile.html', {
        'student': student_profile,
        'enrollments': enrollments,
        'teacher_courses': teacher_courses,
        'title': 'Личный кабинет'
    })

@login_required
def profile_edit_view(request):
    #Редактирование профиля
    student_profile = get_object_or_404(Student, user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=student_profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=student_profile, user=request.user)
    return render(request, 'fefu_lab/registration/profile_edit.html', {
        'form': form,
        'title': 'Редактирование профиля'
    })

@login_required
def password_change_view(request):
    #Смена пароля
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('profile')
    else:
        form = PasswordChangeCustomForm(request.user)
    return render(request, 'fefu_lab/registration/password_change.html', {
        'form': form,
        'title': 'Смена пароля'
    })

#DASHBOARDS

def is_teacher(user):
    #Проверка что пользователь преподаватель
    try:
        return user.student_profile.role == 'TEACHER'
    except Student.DoesNotExist:
        return False

def is_admin(user):
    #Проверка что пользователь администратор
    try:
        return user.student_profile.role == 'ADMIN'
    except Student.DoesNotExist:
        return False

@login_required
@user_passes_test(is_teacher, login_url='/login/')
def teacher_dashboard_view(request):
    #Дашборд преподавателя
    student_profile = request.user.student_profile
    courses = student_profile.courses.all()
    # Собираем статистику по курсам
    course_stats = []
    for course in courses:
        enrollments_count = course.enrollments.filter(status='ACTIVE').count()
        course_stats.append({
            'course': course,
            'enrollments_count': enrollments_count,
            'available_spots': course.max_students - enrollments_count
        })
    return render(request, 'fefu_lab/dashboard/teacher_dashboard.html', {
        'course_stats': course_stats,
        'title': 'Дашборд преподавателя'
    })

@login_required
@user_passes_test(is_admin, login_url='/login/')
def admin_dashboard_view(request):
    #Дашборд администратора
    stats = {
        'total_students': Student.objects.filter(role='STUDENT').count(),
        'total_teachers': Student.objects.filter(role='TEACHER').count(),
        'total_courses': Course.objects.count(),
        'total_enrollments': Enrollment.objects.count(),
        'active_enrollments': Enrollment.objects.filter(status='ACTIVE').count(),
    }
    recent_students = Student.objects.filter(role='STUDENT').order_by('-created_at')[:5]
    recent_courses = Course.objects.order_by('-created_at')[:5]
    return render(request, 'fefu_lab/dashboard/admin_dashboard.html', {
        'stats': stats,
        'recent_students': recent_students,
        'recent_courses': recent_courses,
        'title': 'Панель администратора'
    })

@login_required
def protected_page_view(request):
    #Пример защищенной страницы (только для авторизованных)
    return render(request, 'fefu_lab/protected_page.html', {
        'title': 'Защищенная страница'
    })

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='/login/')
def staff_only_view(request):
    #Пример страницы только для staff
    return render(request, 'fefu_lab/staff_only.html', {
        'title': 'Только для персонала'
    })

def custom_404(request, exception):
    return render(request, 'fefu_lab/404.html', status=404)

def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Сохраняем в базу данных
            Feedback.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                subject=form.cleaned_data['subject'],
                message=form.cleaned_data['message']
            )
            return render(request, 'fefu_lab/success.html', {
                'message': 'Спасибо за feedback.',
                'title': 'Обратная связь'
            })
    else:
        form = FeedbackForm()

    return render(request, 'fefu_lab/feedback.html', {
        'form': form,
        'title': 'Обратная связь'
    })
