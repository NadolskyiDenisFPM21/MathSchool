from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Учень'
        TEACHER = 'teacher', 'Вчитель'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name='Роль'
    )

    teacher = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='students')


    def is_student(self):
        return self.role == self.Role.STUDENT

    def is_teacher(self):
        return self.role == self.Role.TEACHER

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"




class Invite(models.Model):
    code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='sent_invites')
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Запрошення від {self.created_by.username} — {'використано' if self.is_used else 'активне'}"
