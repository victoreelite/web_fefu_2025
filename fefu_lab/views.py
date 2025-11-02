from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.views import View
from .forms import FeedbackForm, RegistrationForm, LoginForm
from .models import UserProfile, Feedback

def home_page(request):
    return render(request, 'fefu_lab/home.html')

def about_page(request):
    return render(request, 'fefu_lab/about.html')

def student_profile(request, student_id):
    if student_id > 100:
        raise Http404("Студент не найден")
    context = {
        'student_id': student_id,
        'student_name': 'Черепанова Виктория',
        'group': f'WEB-{2000 + student_id}',
        'faculty': 'Компьютерная безопасность',
        'course': student_id % 4 + 1,
        'status': 'Активен'
    }
    return render(request, 'fefu_lab/student_profile.html', context)

class CourseView(View):
    def get(self, request, course_slug):
        courses = {
            'python-basic': {
                'title': 'Python Basic',
                'description': 'Курс по программированию на Python',
                'duration': '2 месяца',
                'level': 'Начальный',
                'instructor': 'ghosty6798',
                'price': 'Бесплатно'
            },
            'web-development': {
                'title': 'Web Development',
                'description': 'Курс по веб-разработке на Django.',
                'duration': '3 месяца',
                'level': 'Средний',
                'instructor': 'floyloy3445',
                'price': '2 чизбургера + кола (без сахара)'
            }
        }
        course = courses.get(course_slug)
        if not course:
            raise Http404("Курс не найден")
        context = {
            'course': course,
            'course_slug': course_slug
        }
        return render(request, 'fefu_lab/course_detail.html', context)

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