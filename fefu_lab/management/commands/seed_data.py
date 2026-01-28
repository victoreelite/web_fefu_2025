from django.core.management.base import BaseCommand
from django.utils import timezone
from fefu_lab.models import Student, Instructor, Course, Enrollment
from datetime import date, timedelta
import random

class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными для университета'
    def handle(self, *args, **options):
        self.stdout.write('Начинаю заполнение базы данных тестовыми данными...')
        # Очистка существующих данных!
        Enrollment.objects.all().delete()
        Course.objects.all().delete()
        Student.objects.all().delete()
        Instructor.objects.all().delete()
        self.stdout.write('Создание преподавателей...')
        instructors = [
            Instructor(
                first_name='Анна',
                last_name='Иванова',
                email='a.ivanova@fefu.ru',
                specialization='Кибербезопасность и криптография',
                degree='Доктор технических наук'
            ),
            Instructor(
                first_name='Михаил',
                last_name='Петров',
                email='m.petrov@fefu.ru',
                specialization='Веб-технологии и разработка',
                degree='Кандидат технических наук'
            ),
            Instructor(
                first_name='Ольга',
                last_name='Сидорова',
                email='o.sidorova@fefu.ru',
                specialization='Искусственный интеллект и машинное обучение',
                degree='Доктор физико-математических наук'
            ),
        ]
        for instructor in instructors:
            instructor.save()
            self.stdout.write(f'  Создан: {instructor}')
        self.stdout.write('Создание студентов...')
        students_data = [
            ('Дмитрий', 'Смирнов', 'd.smirnov@fefu.ru', date(2000, 5, 15), 'CS'),
            ('Екатерина', 'Кузнецова', 'e.kuznetsova@fefu.ru', date(2001, 8, 22), 'IT'),
            ('Артем', 'Попов', 'a.popov@fefu.ru', date(1999, 3, 10), 'SE'),
            ('София', 'Васильева', 's.vasilyeva@fefu.ru', date(2002, 11, 5), 'DS'),
            ('Иван', 'Новиков', 'i.novikov@fefu.ru', date(2000, 12, 30), 'WEB'),
            ('Анастасия', 'Морозова', 'a.morozova@fefu.ru', date(2001, 7, 18), 'CS'),
            ('Кирилл', 'Волков', 'k.volkov@fefu.ru', date(1999, 9, 25), 'IT'),
            ('Мария', 'Алексеева', 'm.alekseeva@fefu.ru', date(2000, 4, 12), 'SE'),
        ]
        students = []
        for first_name, last_name, email, birth_date, faculty in students_data:
            student = Student(
                first_name=first_name,
                last_name=last_name,
                email=email,
                birth_date=birth_date,
                faculty=faculty
            )
            student.save()
            students.append(student)
            self.stdout.write(f'  Создан: {student}')
        self.stdout.write('Создание курсов...')
        courses_data = [
            ('Основы Python для начинающих', 'python-basics',
             'Базовый курс по программированию на Python. Изучение синтаксиса, типов данных и основных конструкций языка.',
             36, instructors[0], 'BEGINNER', 25, 0),
            ('Продвинутая кибербезопасность', 'cybersecurity-advanced',
             'Изучение современных методов защиты информации: криптография, анализ уязвимостей, пентестинг.',
             48, instructors[0], 'ADVANCED', 20, 15000),
            ('Веб-разработка на Django', 'django-web-dev',
             'Полный курс по созданию веб-приложений с использованием Django, REST API и современных фронтенд-технологий.',
             42, instructors[1], 'INTERMEDIATE', 30, 12000),
            ('Машинное обучение на практике', 'ml-practice',
             'Прикладной курс по машинному обучению: от предобработки данных до deployment моделей.',
             40, instructors[2], 'ADVANCED', 15, 18000),
            ('JavaScript и современные фреймворки', 'js-frameworks',
             'Изучение современного JavaScript и популярных фреймворков: React, Vue.js, Angular.',
             35, instructors[1], 'INTERMEDIATE', 25, 10000),
        ]
        courses = []
        for title, slug, description, duration, instructor, level, max_students, price in courses_data:
            course = Course(
                title=title,
                slug=slug,
                description=description,
                duration=duration,
                instructor=instructor,
                level=level,
                max_students=max_students,
                price=price
            )
            course.save()
            courses.append(course)
            self.stdout.write(f'  Создан: {course}')
        self.stdout.write('Создание записей на курсы...')
        enrollments = []
        # Каждый студент записывается на 1-3 случайных курса
        for student in students:
            num_courses = random.randint(1, 3)
            selected_courses = random.sample(courses, min(num_courses, len(courses)))
            for course in selected_courses:
                enrollment = Enrollment(
                    student=student,
                    course=course,
                    status='ACTIVE'
                )
                enrollment.save()
                enrollments.append(enrollment)
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Успешно создано:\n'
                f'   • {len(instructors)} преподавателей\n'
                f'   • {len(students)} студентов\n'
                f'   • {len(courses)} курсов\n'
                f'   • {len(enrollments)} записей на курсы\n'
                f'\nДля просмотра данных:\n'
                f'1. Запустить сервер: python manage.py runserver\n'
                f'2. Открыть http://127.0.0.1:8000/\n'
                f'3. Админка: http://127.0.0.1:8000/admin/\n'
                f'   (логин: созданный при createsuperuser)'
            )
        )