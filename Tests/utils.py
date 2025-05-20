from rest_framework.exceptions import ValidationError
from .serializers import TestSerializer

import openai
import os
import json
from dotenv import load_dotenv
load_dotenv()

def generate_test_data(test_data: dict):
    serializer = TestSerializer(data=test_data)
    if serializer.is_valid():
        test_instance = serializer.save()
        return test_instance.test_link
    else:
        raise ValidationError(serializer.errors)


def generate_test_via_openai(prompt: str, api_key: str = None):
    client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": "Ти генератор JSON-даних для створення тестів у Django. Твоя відповідь повинна бути у вигляді виклику функції generate_test_data."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "generate_test_data",
                    "description": "Генерує JSON для створення тесту з питаннями.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": { "type": "string" },
                            "description": { "type": "string" },
                            "questions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "question_type": {
                                            "type": "string",
                                            "enum": ["text", "choice", "match"]
                                        },
                                        "text": { "type": "string" },
                                        "correct_answer": { "type": "string" },
                                        "choices": {
                                            "type": "array",
                                            "items": { "type": "string" }
                                        },
                                        "correct_choice": { "type": "integer" },
                                        "left_items": {
                                            "type": "array",
                                            "items": { "type": "string" }
                                        },
                                        "right_items": {
                                            "type": "array",
                                            "items": { "type": "string" }
                                        },
                                        "correct_pairs": {
                                            "type": "array",
                                            "items": {
                                                "type": "array",
                                                "items": { "type": "integer" },
                                                "minItems": 2,
                                                "maxItems": 2
                                            }
                                        }
                                    },
                                    "required": ["question_type", "text"]
                                }
                            }
                        },
                        "required": ["title", "description", "questions"]
                    }
                }
            }
        ],
        tool_choice="auto"
    )

    tool_call = response.choices[0].message.tool_calls[0]
    function_args = json.loads(tool_call.function.arguments)
    return function_args
