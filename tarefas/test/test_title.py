from tarefas.models import Task
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from datetime import date
from tarefas.models import Task

class AccountTests(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='rafa', 
            password='rafa')
        self.client.force_authenticate(user=self.user)
    
    def test_title_blank_false(self):
        url = reverse('task-list')
        data = {'descricao': 'Agora vai!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Task.objects.count(), 0) # Tarefa não pode ser criada
        self.assertEqual(response.data['titulo'][0], 'Este campo é obrigatório.')  # Verifica a mensagem de erro
        
    def test_deadline_not_lower_than_2000(self):
        past_date = date(1999, 12, 31)  # Data anterior a 01/01/2000
        data = {
            'titulo': 'Tarefa Teste',
            'prazo': past_date,
            'descricao': 'Descrição da tarefa',
            'finalizada': False
        }

        url = reverse('task-list')  
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Verifica se a requisição retorna um status de erro
        self.assertIn('prazo', response.data)  # Verifica se o campo 'prazo' está presente nos dados de resposta
        self.assertEqual(response.data['prazo'][0], "O prazo não pode ser inferior ao ano 2000.")  # Verifica a mensagem de erro retornada