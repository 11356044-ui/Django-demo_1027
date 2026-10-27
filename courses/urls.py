from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('drop/<int:course_id>/', views.drop_course, name='drop_course'),
    path('my-schedule/', views.my_schedule, name='my_schedule'),
]
