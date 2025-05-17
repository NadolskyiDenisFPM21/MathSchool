import shortuuid
from django.contrib.postgres.fields import ArrayField
from django.db import models

from DjangoGPTMath import settings


class Test(models.Model):
    title = models.CharField(max_length=255, verbose_name="Назва тесту")
    description = models.TextField(blank=True, verbose_name="Опис")
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    test_link = models.URLField(verbose_name='Посилання на тест', blank=True, editable=False)

    def generate_test_link(self):
        return shortuuid.ShortUUID().random(length=8)

    def save(self, *args, **kwargs):
        if not self.test_link:
            self.test_link = self.generate_test_link()

        super().save(*args, **kwargs)


    def __str__(self):
        return self.title


class Question(models.Model):
    class QuestionType(models.TextChoices):
        TEXT = "text", 'Відкрите питання'
        CHOICE = 'choice', 'Вибір відповіді'
        MATCH = 'match', 'Сопоставлення'


    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Питання')
    question_type = models.CharField(max_length=32, choices=QuestionType.choices)

    def get_real_instance(self):
        return getattr(self, self.question_type + "question")


    def __str__(self):
        return self.text


class TextQuestion(Question):
    correct_answer = models.TextField(verbose_name='Правильна відповідь')

    def __str__(self):
        return self.text


class ChoiceQuestion(Question):
    choices = ArrayField(models.TextField(), verbose_name='Варіанти відповідей')
    correct_choice = models.IntegerField(verbose_name='Індекс правильної відповіді')

    def __str__(self):
        return f"[Вибір з варіантів] {self.text}"



class MatchQuestion(Question):
    left_items = ArrayField(
        models.CharField(max_length=255),
        verbose_name="Ліва сторона"
    )
    right_items = ArrayField(
        models.CharField(max_length=255),
        verbose_name="Права сторона"
    )
    correct_pairs = ArrayField(
        base_field=ArrayField(
            models.IntegerField(),
            size=2,
        ),
        help_text="Індекси відповідностей: [[0, 2], [1, 0], ...]",
        verbose_name="Правильні відповідності"
    )

    def __str__(self):
        return f"[Співвідношення] {self.text}"


class TestAttempt(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} — {self.test.title}"


class Answer(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = models.JSONField(verbose_name="Відповідь")

    def __str__(self):
        return f"Відповідь на '{self.question.text}' від {self.attempt.student.username}"
