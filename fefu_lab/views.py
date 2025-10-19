from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.views import View


# Function-Based Views
def home_page(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Главная страница</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>Добро пожаловать на главную страницу!</h1>
        <p>Это главная страница нашего веб-приложения.</p>
        <ul>
            <li><a href="/about/">О нас</a></li>
            <li><a href="/student/1/">Профиль студента 1</a></li>
            <li><a href="/student/2/">Профиль студента 2</a></li>
            <li><a href="/course/python-basic/">Курс Python Basic</a></li>
            <li><a href="/course/web-development/">Курс Web Development</a></li>
        </ul>
    </body>
    </html>
    """
    return HttpResponse(html)


def about_page(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>О нас</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>О нашей компании</h1>
        <p>Мы - ведущий образовательный центр в области IT технологий.</p>
        <p>Наша миссия - предоставлять качественное образование для всех желающих.</p>
        <a href="/">Вернуться на главную</a>
    </body>
    </html>
    """
    return HttpResponse(html)


def student_profile(request, student_id):
    # Простая проверка существования студента
    if student_id > 100:
        raise Http404("Студент не найден")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Профиль студента</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            h1 {{ color: #333; }}
            .info {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
            a {{ color: #007bff; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <h1>Профиль студента</h1>
        <div class="info">
            <p><strong>ID студента:</strong> {student_id}</p>
            <p><strong>Имя:</strong> Студент {student_id}</p>
            <p><strong>Группа:</strong> WEB-{2000 + student_id}</p>
            <p><strong>Статус:</strong> Активен</p>
        </div>
        <br>
        <a href="/">Вернуться на главную</a>
    </body>
    </html>
    """
    return HttpResponse(html)


# Class-Based View для курсов
class CourseView(View):
    def get(self, request, course_slug):
        courses = {
            'python-basic': {
                'title': 'Python Basic',
                'description': 'Базовый курс по программированию на Python',
                'duration': '2 месяца'
            },
            'web-development': {
                'title': 'Web Development',
                'description': 'Курс по веб-разработке с Django',
                'duration': '3 месяца'
            },
            'data-science': {
                'title': 'Data Science',
                'description': 'Введение в науку о данных',
                'duration': '4 месяца'
            }
        }

        course = courses.get(course_slug)
        if not course:
            raise Http404("Курс не найден")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{course['title']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                .info {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
                a {{ color: #007bff; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>{course['title']}</h1>
            <div class="info">
                <p><strong>Название:</strong> {course['title']}</p>
                <p><strong>Описание:</strong> {course['description']}</p>
                <p><strong>Продолжительность:</strong> {course['duration']}</p>
                <p><strong>Slug:</strong> {course_slug}</p>
            </div>
            <br>
            <a href="/">Вернуться на главную</a>
        </body>
        </html>
        """
        return HttpResponse(html)


# Обработчик 404 ошибки
def custom_404(request, exception):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Страница не найдена</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; text-align: center; }
            h1 { color: #dc3545; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>404 - Страница не найдена</h1>
        <p>Извините, запрашиваемая страница не существует.</p>
        <a href="/">Вернуться на главную</a>
    </body>
    </html>
    """
    return HttpResponse(html, status=404)