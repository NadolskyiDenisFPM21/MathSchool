from django.urls import path
from . import views

app_name = 'Tests'

urlpatterns = [
    path('', views.test_list_view, name='test_list'),  # Список тестов
    path('generate_test/', views.generate_test_view, name='generate_test'),
    path('create/', views.test_create_view, name='test_create'),  # Создание теста
    path('delete/<int:test_id>/', views.test_delete_view, name='test_delete'),
    path('<int:test_id>/', views.test_detail_view, name='test_detail'),  # Детали теста (вопросы)
    path('<int:test_id>/results/', views.test_results_table_view, name='test_results'),  # Результаты теста
    path('<int:test_id>/add-question/', views.add_question_view, name='add_question'),
    path('<int:test_id>/delete/<int:question_id>/', views.delete_question_view, name='delete_question'),
]
