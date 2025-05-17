from django import forms
from .models import Test, Question, TextQuestion, MatchQuestion, ChoiceQuestion


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['title', 'description']


class QuestionTypeForm(forms.Form):
    question_type = forms.ChoiceField(
        choices=Question.QuestionType.choices,
        label="Тип питання"
    )


class BaseQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text']


class TextQuestionForm(BaseQuestionForm):
    class Meta(BaseQuestionForm.Meta):
        model = TextQuestion
        fields = ['text', 'correct_answer']


class ChoiceQuestionForm(BaseQuestionForm):
    choices = forms.CharField(widget=forms.Textarea, help_text="Варіанти через новий рядок")
    correct_choice = forms.IntegerField()

    class Meta(BaseQuestionForm.Meta):
        model = ChoiceQuestion
        fields = BaseQuestionForm.Meta.fields + ['choices', 'correct_choice']

    def clean_choices(self):
        # Преобразуем строку в список
        choices = self.cleaned_data.get('choices')
        # Разделяем строку на список по новой строке
        choices_list = choices.splitlines()
        # Убираем пустые строки
        choices_list = [choice.strip() for choice in choices_list if choice.strip()]
        return choices_list

    def save(self, commit=True):
        # Сохраняем в модели ChoiceQuestion
        instance = super().save(commit=False)
        choices_list = self.cleaned_data['choices']
        # Преобразуем список в массив строк для модели
        instance.choices = choices_list
        if commit:
            instance.save()
        return instance



class MatchQuestionForm(BaseQuestionForm):
    left_items = forms.CharField(widget=forms.Textarea, help_text="Ліва сторона: через новий рядок")
    right_items = forms.CharField(widget=forms.Textarea, help_text="Права сторона: через новий рядок")
    correct_pairs = forms.CharField(widget=forms.Textarea, help_text="Правильні пари: наприклад: 0-2,1-0,...")

    class Meta(BaseQuestionForm.Meta):
        model = MatchQuestion
        fields = BaseQuestionForm.Meta.fields + ['left_items', 'right_items', 'correct_pairs']

    def clean_left_items(self):
        # Преобразуем строку в список
        left_items = self.cleaned_data.get('left_items')
        left_items_list = left_items.splitlines()
        left_items_list = [item.strip() for item in left_items_list if item.strip()]
        return left_items_list

    def clean_right_items(self):
        # Преобразуем строку в список
        right_items = self.cleaned_data.get('right_items')
        right_items_list = right_items.splitlines()
        right_items_list = [item.strip() for item in right_items_list if item.strip()]
        return right_items_list

    def clean_correct_pairs(self):
        # Преобразуем строку вида "0-2,1-0" в список пар
        correct_pairs = self.cleaned_data.get('correct_pairs')
        pairs_list = correct_pairs.splitlines()
        parsed_pairs = []
        for pair in pairs_list:
            try:
                left, right = pair.split('-')
                parsed_pairs.append([int(left.strip()), int(right.strip())])
            except ValueError:
                raise forms.ValidationError("Невірний формат пари. Використовуйте формат 0-2,1-0,...")
        return parsed_pairs

    def save(self, commit=True):
        # Сохраняем в модели MatchQuestion
        instance = super().save(commit=False)
        instance.left_items = self.cleaned_data['left_items']
        instance.right_items = self.cleaned_data['right_items']
        instance.correct_pairs = self.cleaned_data['correct_pairs']
        if commit:
            instance.save()
        return instance
