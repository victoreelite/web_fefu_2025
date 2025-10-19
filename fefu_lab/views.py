from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views import View

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