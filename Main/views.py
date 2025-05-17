import uuid

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from Tests.models import Test, TestAttempt, Question, Answer
from Users.models import User, Invite


@login_required
def index(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return render(request=request, template_name='Main/index.html')




@login_required
def students_view(request: HttpRequest) -> HttpResponse:
    if not request.user.is_teacher():
        return redirect('profile')

    students = request.user.students.all()

    invite_link = None
    # Если в запросе есть параметр invite, то генерируем ссылку
    if request.method == 'POST':
        # Генерация уникального кода
        invite_code = uuid.uuid4()
        # Создаем запись в базе данных для Invite
        invite = Invite.objects.create(code=invite_code, created_by=request.user)

        invite_link = request.build_absolute_uri(reverse('Users:register_student', args=[invite.code]))

    return render(request, 'teacher/students.html', {'students': students, 'invite_link': invite_link})


@login_required
def start_testing_view(request: HttpRequest, test_link) -> HttpResponse:
    test = Test.objects.filter(test_link=test_link).first()
    if not test:
        return redirect('Main:home')
    return render(request, 'Main/start_testing.html', {'test': test, 'student': request.user})


@login_required
def testing_view(request: HttpRequest, test_link, student_id) -> HttpResponse:
    test = get_object_or_404(Test, test_link=test_link)
    questions = test.question_set.all()

    if request.method == "POST":
        attempt = TestAttempt.objects.create(student=request.user, test=test)

        for question in questions:
            input_data = request.POST.get(f"question_{question.id}", "").strip()

            # Обработка в зависимости от типа вопроса
            if question.question_type == Question.QuestionType.MATCH:
                # Приводим строку сопоставлений к стандартному виду
                response = input_data  # пример: "0-2,1-0"
            elif question.question_type == Question.QuestionType.CHOICE:
                response = input_data  # номер выбранного варианта
            else:  # text
                response = input_data

            Answer.objects.create(
                attempt=attempt,
                question=question,
                response=response
            )

        attempt.finished_at = timezone.now()
        attempt.save()
        return redirect('Main:attempt_results', attempt_id=attempt.id)

    return render(request, 'Main/testing.html', {
        'test': test,
        'questions': questions
    })


@login_required
def attempt_results_view(request, attempt_id):
    def normalize_pairs(pairs_str):
        result = []
        if not pairs_str:
            return result
        pairs = pairs_str.split(",")
        for pair in pairs:
            try:
                left, right = map(int, pair.strip().split("-"))
                result.append([left, right])
            except ValueError:
                continue
        return result

    attempt = get_object_or_404(TestAttempt, pk=attempt_id, student=request.user)
    answers = Answer.objects.filter(attempt=attempt).select_related('question')
    total_questions = answers.count()
    correct_count = 0

    detailed_results = []

    for answer in answers:
        base_question = answer.question
        question = base_question.get_real_instance()
        is_correct = False
        your_answer = answer.response

        if question.question_type == Question.QuestionType.TEXT:
            is_correct = str(your_answer).strip().lower() == question.correct_answer.strip().lower()

        elif question.question_type == Question.QuestionType.CHOICE:
            try:
                is_correct = int(your_answer) == question.correct_choice
            except (ValueError, TypeError):
                is_correct = False

        elif question.question_type == Question.QuestionType.MATCH:
            # Преобразование ответа в список пар, если это строка
            if isinstance(your_answer, str):
                your_pairs = normalize_pairs(your_answer)
                print(your_pairs)
            else:
                your_pairs = your_answer  # если уже список
            is_correct = sorted(your_pairs) == sorted(question.correct_pairs)
            your_answer = your_pairs  # сохраняем для шаблона

        if is_correct:
            correct_count += 1

        detailed_results.append({
            'question': question,             # Это уже MatchQuestion / ChoiceQuestion и т.д.
            'your_answer': your_answer,       # Уже list для MatchQuestion
            'is_correct': is_correct,
        })

    score = f"{correct_count} / {total_questions}" if total_questions else "—"

    


    return render(request, 'Main/attempt_results.html', {
        'attempt': attempt,
        'results': detailed_results,
        'score': score,
    })