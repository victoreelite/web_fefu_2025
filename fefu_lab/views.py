from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.views import View
from .forms import FeedbackForm, RegistrationForm, LoginForm
from .models import UserProfile, Feedback, Student, Course, Instructor, Enrollment

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

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Сохраняем пользователя
            UserProfile.objects.create(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            return render(request, 'fefu_lab/success.html', {
                'message': 'Регистрация прошла успешно.',
                'title': 'Регистрация'
            })
    else:
        form = RegistrationForm()

    return render(request, 'fefu_lab/register.html', {
        'form': form,
        'title': 'Регистрация'
    })

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Проверяем существование пользователя
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = UserProfile.objects.get(username=username, password=password)
                return render(request, 'fefu_lab/success.html', {
                    'message': f'Вход выполнен успешно. Добро пожаловать, {user.username}.',
                    'title': 'Вход в систему'
                })
            except UserProfile.DoesNotExist:
                form.add_error(None, 'Неверный логин или пароль')
    else:
        form = LoginForm()

    return render(request, 'fefu_lab/login.html', {
        'form': form,
        'title': 'Вход в систему'
    })