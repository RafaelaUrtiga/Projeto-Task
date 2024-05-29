from rest_framework import serializers
from .models import Task
from datetime import date
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password',]

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        
  
    def validate_prazo(self, prazo):
        if prazo < date(2000, 1, 1):
            raise serializers.ValidationError("O prazo não pode ser inferior ao ano 2000.")
        return prazo