from django.urls import path
from .views import index, students_view, testing_view, start_testing_view, attempt_results_view, chat_interface_view, \
    chat_api_view

app_name = "Main"

urlpatterns = [
    path('', index, name='home'),
    path('students', students_view, name='students'),
    path('test/<str:test_link>', start_testing_view, name='start_testing'),
    path('test/<str:test_link>/<int:student_id>', testing_view, name='testing'),
    path('test/results/<int:attempt_id>/', attempt_results_view, name='attempt_results'),
    path('ai/chat/', chat_interface_view, name='chat'),
    path('ai/chat/generate_answer/<str:thread_id>/', chat_api_view, name='chat_api')
]