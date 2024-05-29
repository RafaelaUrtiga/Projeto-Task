from django.urls import path
from .views import TaskList, TaskDetail, ExportTasks, TaskReports
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('tarefas/', TaskList.as_view(), name='task-list'),
    path('tarefas/<int:id>/', TaskDetail.as_view(), name='task-detail'),
    path('export/', ExportTasks.as_view(), name='task-export'),
    path('report/<str:report_type>/', TaskReports.as_view(), name='task-report')
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'txt'])
