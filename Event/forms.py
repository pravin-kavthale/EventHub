# forms.py
from django import forms
from .models import Category,Comment  # use Category, not EventCategory

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'favicon']  # slug is auto
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter category description'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter category name'}),
        }
class commentForm(forms.ModelForm):
    class Meta:
        model=Comment
        fields=['content']
        widget={
            'content': forms.TextInput(attrs={
                'class': 'form-control form-control-sm rounded-pill',
                'placeholder': 'Edit your comment'
            }),
        }