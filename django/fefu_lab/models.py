from django.db import models
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Instructor(models.Model):
    #Модель преподавателя
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(unique=True, verbose_name='Email')
    specialization = models.CharField(max_length=200, verbose_name='Специализация')
    degree = models.CharField(max_length=100, blank=True, verbose_name='Ученая степень')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
        ordering = ['last_name', 'first_name']
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Student(models.Model):
    #Модель студента
    FACULTY_CHOICES = [
        ('CS', 'Кибербезопасность'),
        ('SE', 'Программная инженерия'),
        ('IT', 'Информационные технологии'),
        ('DS', 'Наука о данных'),
        ('WEB', 'Веб-технологии'),
    ]
    ROLE_CHOICES = [
        ('STUDENT', 'Студент'),
        ('TEACHER', 'Преподаватель'),
        ('ADMIN', 'Администратор'),
    ]
    # Связь со встроенной моделью User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name='Пользователь',
        null=True,  # Временно null для миграции
        blank=True
    )
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(unique=True, verbose_name='Email')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    faculty = models.CharField(
        max_length=3,
        choices=FACULTY_CHOICES,
        default='CS',
        verbose_name='Факультет'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='STUDENT',
        verbose_name='Роль'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    bio = models.TextField(blank=True, verbose_name='О себе')
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        ordering = ['last_name', 'first_name']
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    @property
    def full_name(self):
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}"
        return f"{self.first_name} {self.last_name}"
    def get_absolute_url(self):
        return reverse('profile')
    def is_teacher(self):
        return self.role == 'TEACHER'
    def is_admin(self):
        return self.role == 'ADMIN'
    def get_faculty_display_name(self):
        return dict(self.FACULTY_CHOICES).get(self.faculty, 'Неизвестно')

# Сигнал для автоматического создания профиля при создании User
@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created:
        Student.objects.create(
            user=instance,
            first_name=instance.first_name or '',
            last_name=instance.last_name or '',
            email=instance.email or '',
            # Устанавливаем роль staff/superuser в админы
            role='ADMIN' if (instance.is_staff or instance.is_superuser) else 'STUDENT'
        )

@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    if hasattr(instance, 'student_profile'):
        instance.student_profile.save()

class Course(models.Model):
    #Модель курса
    LEVEL_CHOICES = [
        ('BEGINNER', 'Начальный'),
        ('INTERMEDIATE', 'Средний'),
        ('ADVANCED', 'Продвинутый'),
    ]
    title = models.CharField(max_length=200, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL-адрес')
    description = models.TextField(verbose_name='Описание')
    duration = models.IntegerField(verbose_name='Продолжительность (часов)')
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
        verbose_name='Преподаватель'
    )
    level = models.CharField(
        max_length=12,
        choices=LEVEL_CHOICES,
        default='BEGINNER',
        verbose_name='Уровень сложности'
    )
    max_students = models.IntegerField(default=30, verbose_name='Макс. студентов')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Стоимость'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['title']
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'slug': self.slug})

class Enrollment(models.Model):
    #Модель записи на курс
    STATUS_CHOICES = [
        ('ACTIVE', 'Активна'),
        ('COMPLETED', 'Завершена'),
        ('CANCELLED', 'Отменена'),
    ]
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Студент'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Курс'
    )
    enrollment_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата записи')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        verbose_name='Статус'
    )
    class Meta:
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курсы'
        unique_together = ['student', 'course']  # Один студент не может записаться дважды
    def __str__(self):
        return f"{self.student} → {self.course}"

class UserProfile(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.username

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.subject} - {self.name}"