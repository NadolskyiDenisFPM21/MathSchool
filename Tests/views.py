import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from Users.models import User
from .models import Test, TestAttempt, Answer, Question, ChoiceQuestion
from django.contrib.auth.decorators import login_required
from .forms import TestForm, ChoiceQuestionForm, MatchQuestionForm, BaseQuestionForm, QuestionTypeForm, TextQuestionForm
from django.forms import modelformset_factory

from .utils import generate_test_via_openai, generate_test_data


@login_required
def test_list_view(request):
    if request.user.role == User.Role.STUDENT:
        return redirect('Main:home')
    tests = Test.objects.all()
    return render(request, 'tests/test_list.html', {'tests': tests})


@login_required
def test_detail_view(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    base_questions = test.questions.all()

    test_url = f"{request.build_absolute_uri('/test/')}{test.test_link}"
    # Преобразуем базовые вопросы в их подклассы
    questions = []
    for q in base_questions:
        if hasattr(q, 'choicequestion'):
            questions.append(q.choicequestion)
        elif hasattr(q, 'matchquestion'):
            questions.append(q.matchquestion)
        elif hasattr(q, 'textquestion'):
            questions.append(q.textquestion)
        else:
            questions.append(q)  # fallback

    return render(request, 'Tests/test_detail.html', {
        'test': test,
        'questions': questions,
        'test_url': test_url,
    })


@login_required
def test_create_view(request):
    TestFormSet = modelformset_factory(Test, form=TestForm, extra=1)
    if request.method == "POST":
        formset = TestFormSet(request.POST)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for inst in instances:
                inst.author = request.user
                inst.save()
            return redirect('Tests:test_list')
    else:
        formset = TestFormSet(queryset=Test.objects.none())
    return render(request, 'tests/test_create.html', {'formset': formset})


@login_required
def test_delete_view(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    if request.method == "POST":
        test.delete()
    return redirect('Tests:test_list')


@login_required
def test_results_table_view(request, test_id):
    test = get_object_or_404(Test, pk=test_id)
    attempts = TestAttempt.objects.filter(test=test).select_related('student')
    return render(request, 'tests/test_results_table.html', {'test': test, 'attempts': attempts})


def add_question_view(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    question_type = request.GET.get("question_type")

    form_class = {
        Question.QuestionType.CHOICE: ChoiceQuestionForm,
        Question.QuestionType.MATCH: MatchQuestionForm,
        Question.QuestionType.TEXT: TextQuestionForm,
    }.get(question_type)

    if not form_class:
        return redirect('Tests:test_detail', test_id=test_id)

    if request.method == "POST":
        form = form_class(request.POST)
        print(form.errors)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.test = test
            instance.question_type = question_type

            # Для MatchQuestion вручную устанавливаем поля, которые обрабатываются в форме
            if isinstance(form, MatchQuestionForm):
                instance.left_items = form.cleaned_data['left_items']
                instance.right_items = form.cleaned_data['right_items']
                instance.correct_pairs = form.cleaned_data['correct_pairs']

            # Для ChoiceQuestion тоже вручную:
            if isinstance(form, ChoiceQuestionForm):
                instance.choices = form.cleaned_data['choices']
                instance.correct_choice = form.cleaned_data['correct_choice']

            instance.save()
            return redirect('Tests:test_detail', test_id=test_id)
    else:
        form = form_class()

    return render(request, 'Tests/add_question.html', {
        'test': test,
        'form': form,
        'question_type': question_type,
    })


def delete_question_view(request, test_id, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        question.delete()
        return redirect('Tests:test_detail', test_id=test_id)
    return redirect('Tests:test_detail', test_id=test_id)


@login_required
def generate_test_view(request):
    if request.method == "POST":
        topic = request.POST.get("topic")
        difficulty = request.POST.get("difficulty")
        test_data = generate_test_via_openai(f"Згенеруй тест на тему:{topic} і складністю: {difficulty} з 10")
        test_link = generate_test_data(test_data)
        return redirect('Main:start_testing', test_link=test_link)
    return render(request, 'tests/generate_test.html')



def test_api(request):
    test_data = generate_test_via_openai("Згенеруй практичний тест на тему: Квадратні рівняння")
    test_link = generate_test_data(test_data)
    return HttpResponse(test_link)


