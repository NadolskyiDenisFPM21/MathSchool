import time
import uuid

import openai
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from DjangoGPTMath import settings
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
    questions = test.questions.all()

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



# View для рендеру чату
@login_required
def chat_interface_view(request):
    openai.api_key = settings.OPENAI_API_KEY
    thread = openai.beta.threads.create()
    return render(request, 'Main/gpt_chat.html', {'thread_id': thread.id})


@csrf_exempt
@require_POST
def chat_api_view(request, thread_id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Authentication required"}, status=403)

    message = request.POST.get('message', '').strip()
    image = request.FILES.get('image')

    if not message:
        return JsonResponse({"error": "Message cannot be empty"}, status=400)

    # Отримати відповідь від ШІ
    reply = generate_ai_reply(message, image, thread_id=thread_id)

    return JsonResponse({"reply": reply})

def generate_ai_reply(message, image=None, thread_id=None):
    # Якщо є зображення — завантажити його
    file_id = None
    if image:
        uploaded_file = openai.files.create(
            file=(image.name, image),
            purpose="assistants"
        )
        file_id = uploaded_file.id

    # Додати повідомлення користувача
    message_payload = {
        "thread_id": thread_id,
        "role": "user",
        "content": message,
    }
    if file_id:
        message_payload["file_ids"] = [file_id]

    openai.beta.threads.messages.create(**message_payload)

    # Запустити асистента
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=settings.ASSISTANT_ID,
        stream=False
    )

    # Дочекатись завершення run
    while run.status not in ["completed", "failed", "cancelled"]:
        time.sleep(1)
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )

    if run.status != "completed":
        return "⚠️ Помилка під час обробки запиту ШІ."

    # Отримати повідомлення асистента
    messages = openai.beta.threads.messages.list(thread_id=thread_id)
    print(messages)
    for msg in messages.data:
        if msg.role == "assistant":
            parts = msg.content
            reply = "".join(part.text.value for part in parts if part.type == "text")
            return reply

    return "⚠️ ШІ не надав відповіді."