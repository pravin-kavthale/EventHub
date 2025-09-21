# forms.py
from django import forms
from .models import Category  # use Category, not EventCategory

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'favicon']  # slug is auto
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter category description'}),
            'name': forms.TextInput(attrs={'placeholder': 'Enter category name'}),
        }