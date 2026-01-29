from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from fefu_lab.models import Student, Instructor, Course, Enrollment
from datetime import date
import random

class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write('Начинаю заполнение базы данных...')
        # Отключаем сигналы
        from fefu_lab.models import create_student_profile, save_student_profile
        post_save.disconnect(create_student_profile, sender=User)
        post_save.disconnect(save_student_profile, sender=User)
        try:
            self.stdout.write('Очистка старых данных...')
            # 1. Удаляем
            Enrollment.objects.all().delete()
            Course.objects.all().delete()
            Instructor.objects.all().delete()
            Student.objects.all().delete()
            # 2. Удаляем всех пользователей
            User.objects.all().delete()
            # 3. Создаем студентов
            self.stdout.write('\nСОЗДАЕМ СТУДЕНТОВ...')
            students_data = [
                ('Анна', 'Иванова', 'anna.ivanova@fefu.ru', date(2000, 5, 15), 'CS', 'student123'),
                ('Дмитрий', 'Смирнов', 'dmitry.smirnov@fefu.ru', date(1999, 8, 22), 'SE', 'student123'),
                ('Екатерина', 'Попова', 'ekaterina.popova@fefu.ru', date(2001, 3, 10), 'IT', 'student123'),
                ('Михаил', 'Васильев', 'mikhail.vasilyev@fefu.ru', date(2000, 11, 5), 'DS', 'student123'),
                ('Ольга', 'Новикова', 'olga.novikova@fefu.ru', date(1999, 12, 30), 'WEB', 'student123'),
            ]
            students = []
            for first_name, last_name, email, birth_date, faculty, password in students_data:
                # Создаём пользователя
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=True
                )
                # Теперь создаём Student вручную
                student = Student.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    birth_date=birth_date,
                    faculty=faculty,
                    role='STUDENT',
                    phone=f'+7 914 {random.randint(100, 999)} {random.randint(1000, 9999)}',
                    bio=f'Студент факультета {faculty}',
                    is_active=True
                )
                students.append(student)
                self.stdout.write(f'✓ Студент: {email} / {password}')
            # 4. Создаем преподавателей
            self.stdout.write('\nСОЗДАЕМ ПРЕПОДАВАТЕЛЕЙ...')
            teachers_data = [
                ('Иван', 'Петров', 'i.petrov@fefu.ru', 'Кибербезопасность', 'Доктор наук', 'teacher123'),
                ('Мария', 'Сидорова', 'm.sidorova@fefu.ru', 'Веб-разработка', 'Кандидат наук', 'teacher123'),
                ('Алексей', 'Козлов', 'a.kozlov@fefu.ru', 'Сетевые технологии', 'Кандидат наук', 'teacher123'),
            ]
            instructors = []
            for first_name, last_name, email, specialization, degree, password in teachers_data:
                # Создаём пользователя
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    is_active=True
                )
                # Создаём Student с ролью TEACHER
                Student.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    faculty='CS',
                    role='TEACHER',
                    phone=f'+7 914 {random.randint(100, 999)} {random.randint(1000, 9999)}',
                    bio=f'Преподаватель {specialization}',
                    is_active=True
                )
                # Создаём Instructor для курсов
                instructor = Instructor.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    specialization=specialization,
                    degree=degree,
                    is_active=True
                )
                instructors.append(instructor)
                self.stdout.write(f'✓ Преподаватель: {email} / {password}')
            # 5. Создаем курсы
            self.stdout.write('\nСОЗДАЕМ КУРСЫ...')
            courses_data = [
                ('Основы Python', 'python-basics', 'Базовый курс Python',
                 36, instructors[0], 'BEGINNER', 25, 0),
                ('Веб-разработка на Django', 'django-web', 'Создание веб-приложений',
                 48, instructors[1], 'INTERMEDIATE', 20, 12000),
                ('Сетевая безопасность', 'network-security', 'Защита сетей',
                 40, instructors[2], 'ADVANCED', 15, 15000),
            ]
            courses = []
            for title, slug, description, hours, instructor, level, max_students, price in courses_data:
                course = Course.objects.create(
                    title=title,
                    slug=slug,
                    description=description,
                    duration=hours,
                    instructor=instructor,
                    level=level,
                    max_students=max_students,
                    price=price,
                    is_active=True
                )
                courses.append(course)
                self.stdout.write(f'✓ Курс: {title}')
            # 6. Записи на курсы
            self.stdout.write('\n=== ЗАПИСИ НА КУРСЫ ===')
            enrollments = []
            for student in students:
                num = random.randint(1, 2)
                selected = random.sample(courses, min(num, len(courses)))
                for course in selected:
                    enrollment = Enrollment.objects.create(
                        student=student,
                        course=course,
                        status='ACTIVE'
                    )
                    enrollments.append(enrollment)
                self.stdout.write(f'✓ {student.first_name} записан на {len(selected)} курс(ов)')
            # 7. Администратор
            self.stdout.write('\nСОЗДАЕМ АДМИНИСТРАТОРА...')
            admin_user = User.objects.create_user(
                username='admin@fefu.ru',
                email='admin@fefu.ru',
                password='admin123',
                first_name='Админ',
                last_name='Системы',
                is_staff=True,
                is_active=True
            )
            Student.objects.create(
                user=admin_user,
                first_name='Админ',
                last_name='Системы',
                email='admin@fefu.ru',
                faculty='CS',
                role='ADMIN',
                phone='+7 999 123 4567',
                bio='Системный администратор',
                is_active=True
            )
            self.stdout.write(f'✓ Администратор: admin@fefu.ru / admin123')
            # 8. Включаем сигналы
            post_save.connect(create_student_profile, sender=User)
            post_save.connect(save_student_profile, sender=User)
            self.stdout.write(self.style.SUCCESS(
                'Скрипт выполнен. Тестовые данные для входа:\n'
                '1. anna.ivanova@fefu.ru / student123\n'
                '2. i.petrov@fefu.ru / teacher123\n'
                '3. admin@fefu.ru / admin123'
            ))
            self.stdout.write('=' * 50)
        except Exception as e:
            post_save.connect(create_student_profile, sender=User)
            post_save.connect(save_student_profile, sender=User)
            self.stdout.write(self.style.ERROR(f'❌ ОШИБКА: {e}'))
            raise