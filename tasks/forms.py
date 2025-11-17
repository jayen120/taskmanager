from django import forms
from tasks.models import *

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'priority', 'status']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }