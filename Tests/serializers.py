from rest_framework import serializers
from .models import Test, Question, TextQuestion, ChoiceQuestion, MatchQuestion


class BaseQuestionSerializer(serializers.ModelSerializer):
    question_type = serializers.CharField()

    class Meta:
        model = Question
        fields = ['question_type', 'text']


class TextQuestionSerializer(BaseQuestionSerializer):
    correct_answer = serializers.CharField()

    class Meta(BaseQuestionSerializer.Meta):
        model = TextQuestion
        fields = BaseQuestionSerializer.Meta.fields + ['correct_answer']


class ChoiceQuestionSerializer(BaseQuestionSerializer):
    choices = serializers.ListField(child=serializers.CharField())
    correct_choice = serializers.IntegerField()

    class Meta(BaseQuestionSerializer.Meta):
        model = ChoiceQuestion
        fields = BaseQuestionSerializer.Meta.fields + ['choices', 'correct_choice']


class MatchQuestionSerializer(BaseQuestionSerializer):
    left_items = serializers.ListField(child=serializers.CharField())
    right_items = serializers.ListField(child=serializers.CharField())
    correct_pairs = serializers.ListField(
        child=serializers.ListField(
            child=serializers.IntegerField(), min_length=2, max_length=2
        )
    )

    class Meta(BaseQuestionSerializer.Meta):
        model = MatchQuestion
        fields = BaseQuestionSerializer.Meta.fields + ['left_items', 'right_items', 'correct_pairs']


class QuestionPolymorphicSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        q_type = data.get("question_type")
        if q_type == "text":
            return TextQuestionSerializer().to_internal_value(data)
        elif q_type == "choice":
            return ChoiceQuestionSerializer().to_internal_value(data)
        elif q_type == "match":
            return MatchQuestionSerializer().to_internal_value(data)
        else:
            raise serializers.ValidationError(f"Unknown question type: {q_type}")

    def to_representation(self, instance):
        if isinstance(instance, TextQuestion):
            return TextQuestionSerializer(instance).data
        elif isinstance(instance, ChoiceQuestion):
            return ChoiceQuestionSerializer(instance).data
        elif isinstance(instance, MatchQuestion):
            return MatchQuestionSerializer(instance).data
        return super().to_representation(instance)


class TestSerializer(serializers.ModelSerializer):
    questions = QuestionPolymorphicSerializer(many=True)

    class Meta:
        model = Test
        fields = ['title', 'description', 'questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        test = Test.objects.create(**validated_data)

        for q_data in questions_data:
            q_type = q_data['question_type']
            q_data['test'] = test

            if q_type == 'text':
                TextQuestion.objects.create(**q_data)
            elif q_type == 'choice':
                ChoiceQuestion.objects.create(**q_data)
            elif q_type == 'match':
                MatchQuestion.objects.create(**q_data)
        return test
