from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('about/', views.about_page, name='about'),
    path('student/<int:student_id>/', views.student_profile, name='student_profile'),
    path('course/<slug:course_slug>/', views.CourseView.as_view(), name='course_detail'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/password/', views.password_change_view, name='password_change'),
    path('dashboard/teacher/', views.teacher_dashboard_view, name='teacher_dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('protected/', views.protected_page_view, name='protected_page'),
    path('staff-only/', views.staff_only_view, name='staff_only'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='fefu_lab/registration/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='fefu_lab/registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='fefu_lab/registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='fefu_lab/registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]

handler404 = 'fefu_lab.views.custom_404'

