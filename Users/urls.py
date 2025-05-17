from django.urls import path
from .views import register_teacher, register_student, invite_list_create

app_name = "Users"

urlpatterns = [
    path('register/teacher/', register_teacher, name='register_teacher'),
    path('register/student/<uuid:code>/', register_student, name='register_student'),
    path('teacher/invites/', invite_list_create, name='teacher_invites'),
]
