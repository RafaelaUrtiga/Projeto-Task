from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Q
from rest_framework import permissions
from.models import Task
from .serializers import TaskSerializer
from django.http import Http404, HttpResponse
import json
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404

class TaskList(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, format=None):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskDetail (APIView):

    def get_object(self, id):
        try:
            return Task.objects.get(id=id)
        except Task.DoesNotExist:
            raise Http404
    
    def get(self, request, id):
        task = self.get_object(id)
        serializer = TaskSerializer(task)
        return Response(serializer.data)
    
    def put(self, request, id, format=None):
        task = self.get_object(id)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        task = self.get_object(id)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class ExportTasks(APIView):
 
    def get(self, request, format=None):
        tasks = Task.objects.all()
        format = request.GET.get('format')
        
        if format == 'json':
            return self.export_to_json(tasks)
        elif format == 'txt':
            return self.export_to_txt(tasks)
        else:
            return Response({'error': 'Invalid format. Please specify "json" or "txt".'}, status=400)
    
        
    def export_to_json(self, tasks):
        serializer = TaskSerializer(tasks, many=True)
        json_data = json.dumps(serializer.data, indent=4)  # converte o serializer em string
        response = HttpResponse(json_data, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="tasks.json"'
        return response
    
    def export_to_txt(self, tasks):
        content = ''
        for task in tasks:
            serializer_task = TaskSerializer(task).data
            content += (
                f'Titulo: {serializer_task["titulo"]}, '
                f'Descricao: {serializer_task["descricao"]}, '
                f'Prazo: {serializer_task["prazo"]}, '
                f'finalizada: {serializer_task["finalizada"]}, '
                f'criado_por {serializer_task["criado_por"]}, '
                f'finalizada_em {serializer_task["finalizada_em"]}, '
                f'finalizada_por {serializer_task["finalizada_por"]}, '
                f'responsaveis {serializer_task["responsaveis"]}, '
                f'criado_em {serializer_task["criado_em"]}, '
                f'atualizado_em {serializer_task["atualizado_em"]}\n'
            )
        
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="tasks.txt"'
        return response
    

class TaskReports(APIView):
    
    def get_reports (self, request, report_type):
        criada_em = request.GET.get('criada_em')
        finalizada_em = request.GET.get('finalizada_em')
        criado_por = request.GET.get('criado_por')
        finalizado_por = request.GET.get('finalizado_por')
        responsavel = request.GET.get('responsavel')
        
        if not criada_em or not finalizada_em:
            return Response({'error': 'data de criação e data final são obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        try: # coloco no formato desejado
            criada_em = datetime.strptime(criada_em, '%Y-%m-%d').date()
            finalizada_em = datetime.strptime(finalizada_em, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Formato de data inválido. Use AAAA-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        if (finalizada_em - criada_em).days > 365: #condiciono com o ano
            return Response({'error': 'O período entre datas deve ser menor ou igual a 365 dias.'}, status=status.HTTP_400_BAD_REQUEST)


        # Filtros iniciais
        filters = Q(prazo__gte=criada_em) & Q(prazo__lte=finalizada_em)

        if criado_por:
            filters &= Q(criado_por__id=criado_por)
        if finalizado_por:
            filters &= Q(finalizada_por__id=finalizado_por)
        if responsavel:
            filters &= Q(responsaveis__id=responsavel)

        if report_type == 'criadas_finalizadas_por_usuario':
            return self.relatorio_criadas_finalizadas_por_usuario(filters)
        elif report_type == 'atividades_por_responsavel':
            return self.relatorio_atividades_por_responsavel(filters)
        elif report_type == 'atividades_atrasadas_finalizadas_fora_prazo':
            return self.relatorio_atividades_atrasadas_finalizadas_fora_prazo(filters)
        else:
            return Response({'error': 'Tipo de relatório inválido.'}, status=status.HTTP_400_BAD_REQUEST)


    def relatorio_criadas_finalizadas_por_usuario(self, filters):
        criadas = Task.objects.filter(filters).values('criado_por__username').annotate(total_criadas=Count('id'))
        finalizadas = Task.objects.filter(filters & Q(finalizada=True)).values('finalizada_por__username').annotate(total_finalizadas=Count('id'))

        data = {
            'criadas_por_usuario': list(criadas),
            'finalizadas_por_usuario': list(finalizadas)
        }
        return Response(data)


    def relatorio_atividades_por_responsavel(self, filters):
        atividades_por_responsavel = Task.objects.filter(filters).values('responsaveis__username').annotate(total_atividades=Count('id'))

        data = {
            'atividades_por_responsavel': list(atividades_por_responsavel)
        }
        return Response(data)


    def relatorio_atividades_atrasadas_finalizadas_fora_prazo(self, filters):
        hoje = datetime.today().date()
        atrasadas = Task.objects.filter(filters & Q(finalizada=False) & Q(prazo__lt=hoje)).count()
        finalizadas_fora_do_prazo = Task.objects.filter(filters & Q(finalizada=True) & Q(finalizada_em__date__gt=F('prazo'))).count()

        data = {
            'atividades_atrasadas': atrasadas,
            'atividades_finalizadas_fora_do_prazo': finalizadas_fora_do_prazo
        }
        return Response(data)