from django.db import models
from django.contrib.auth.models import User

class Task (models.Model):
    titulo = models.CharField(max_length=255)
    prazo = models.DateField(null=True, blank=True)
    descricao = models.TextField(blank=True)
    finalizada = models.BooleanField(default=False)
    criado_por = models.ForeignKey(User, related_name='tasks_criadas', on_delete=models.CASCADE)
    finalizada_em = models.DateTimeField(null=True, blank=True)
    finalizada_por = models.ForeignKey(User, related_name='tasks_finalizadas', null=True, blank=True, on_delete=models.SET_NULL)
    responsaveis = models.ManyToManyField(User, related_name='tasks_responsaveis')
    criado_em = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.titulo + ': ' + self.descricao
    
class TaskResponsible(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('task', 'user')
        
    def __str__(self):
        return self.task + ': ' + self.user