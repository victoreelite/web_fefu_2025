from django.core.management.base import BaseCommand
from django.utils import timezone
from fefu_lab.models import Student, Instructor, Course, Enrollment
from datetime import date, timedelta
import random
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными для университета'
    def handle(self, *args, **options):
        self.stdout.write('Начинаю заполнение базы данных тестовыми данными...')
        # Очистка существующих данных
        Enrollment.objects.all().delete()
        Course.objects.all().delete()
        Student.objects.all().delete()
        Instructor.objects.all().delete()
        # Удаляем только тестовых пользователей (не суперпользователей)
        test_users = User.objects.filter(
            email__contains='@fefu.ru',
            is_superuser=False,
            is_staff=False
        )
        test_users.delete()
        self.stdout.write('Создание преподавателей и их пользователей...')
        instructors = []
        instructors_data = [
            ('Иван', 'Петров', 'i.petrov@fefu.ru', 'Кибербезопасность и криптография', 'Доктор технических наук'),
            ('Мария', 'Сидорова', 'm.sidorova@fefu.ru', 'Веб-технологии и разработка', 'Кандидат технических наук'),
            ('Ольга', 'Козлова', 'o.kozlova@fefu.ru', 'Искусственный интеллект и машинное обучение',
             'Доктор физико-математических наук'),
        ]
        for first_name, last_name, email, specialization, degree in instructors_data:
            # Создаем пользователя Django
            user = User.objects.create_user(
                username=email,
                email=email,
                password='teacher123',  # Простой пароль для теста
                first_name=first_name,
                last_name=last_name
            )
            # Создаем преподавателя
            instructor = Instructor(
                first_name=first_name,
                last_name=last_name,
                email=email,
                specialization=specialization,
                degree=degree,
                is_active=True
            )
            instructor.save()
            instructors.append(instructor)
            self.stdout.write(f'  Создан преподаватель: {instructor}')
        self.stdout.write('Создание студентов и их пользователей...')
        students = []
        students_data = [
            ('Анна', 'Иванова', 'anna.ivanova@fefu.ru', date(2000, 5, 15), 'CS'),
            ('Дмитрий', 'Смирнов', 'dmitry.smirnov@fefu.ru', date(1999, 8, 22), 'SE'),
            ('Екатерина', 'Попова', 'ekaterina.popova@fefu.ru', date(2001, 3, 10), 'IT'),
            ('Михаил', 'Васильев', 'mikhail.vasilyev@fefu.ru', date(2000, 11, 5), 'DS'),
            ('Ольга', 'Новикова', 'olga.novikova@fefu.ru', date(1999, 12, 30), 'WEB'),
            ('Артем', 'Федоров', 'artem.fedorov@fefu.ru', date(2001, 7, 18), 'CS'),
            ('София', 'Морозова', 'sofia.morozova@fefu.ru', date(2002, 2, 14), 'IT'),
        ]
        for first_name, last_name, email, birth_date, faculty in students_data:
            # Создаем пользователя Django
            user = User.objects.create_user(
                username=email,
                email=email,
                password='user',
                first_name=first_name,
                last_name=last_name
            )
            # Создаем студента
            student = Student(
                user=user,  # Связываем с пользователем
                first_name=first_name,
                last_name=last_name,
                email=email,
                birth_date=birth_date,
                faculty=faculty,
                role='STUDENT',
                phone=f'+7 914 {random.randint(100, 999)} {random.randint(1000, 9999)}',
                bio=f'Студент факультета {dict(Student.FACULTY_CHOICES).get(faculty)}. Увлекаюсь программированием и веб-разработкой.',
                is_active=True
            )
            student.save()
            students.append(student)
            self.stdout.write(f'  Создан студент: {student}')
        self.stdout.write('Создание курсов...')
        courses = []
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
        for title, slug, description, duration, instructor, level, max_students, price in courses_data:
            course = Course(
                title=title,
                slug=slug,
                description=description,
                duration=duration,
                instructor=instructor,
                level=level,
                max_students=max_students,
                price=price,
                is_active=True
            )
            course.save()
            courses.append(course)
            self.stdout.write(f'  Создан курс: {course}')
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
                self.stdout.write(f'  Запись: {student} → {course}')
        # Создаем тестового администратора
        self.stdout.write('Создание тестового администратора...')
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@admin.admin',
            password='admin',
            first_name='Администратор',
            last_name='Системы',
            is_staff=True,
            is_superuser=False
        )

        admin_student = Student(
            user=admin_user,
            first_name='Администратор',
            last_name='Системы',
            email='admin@admin.admin',
            faculty='CS',
            role='ADMIN',
            phone='+7 999 123 4567',
            bio='Системный администратор платформы FEFU Lab',
            is_active=True
        )
        admin_student.save()
        self.stdout.write(
            self.style.SUCCESS(
                f'\nУспешно создано:\n'
                f'   • {len(instructors)} преподавателей с пользователями\n'
                f'   • {len(students)} студентов с пользователями\n'
                f'   • {len(courses)} курсов\n'
                f'   • {len(enrollments)} записей на курсы\n'
                f'   • 1 администратор\n'
                f'\nТестовые учетные данные:\n'
                f'Преподаватели (пароль: teacher123):\n'
                f'   • i.petrov@fefu.ru\n'
                f'   • m.sidorova@fefu.ru\n'
                f'   • o.kozlova@fefu.ru\n'
                f'\nСтуденты (пароль: student123):\n'
                f'   • anna.ivanova@fefu.ru\n'
                f'   • dmitry.smirnov@fefu.ru\n'
                f'   • ekaterina.popova@fefu.ru\n'
                f'   • ... и другие\n'
                f'\nАдминистратор:\n'
                f'   • Логин: admin@fefu.ru\n'
                f'   • Пароль: admin123\n'
                f'\nДля входа используйте email в качестве логина.\n'
            )
        )