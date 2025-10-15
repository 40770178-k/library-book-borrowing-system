from django import forms
from .models import Book, Member, BorrowedBook
from .models import Review
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        exclude = ['user']

class BorrowedBookForm(forms.ModelForm):
    class Meta:
        model = BorrowedBook
        fields = ['member', 'book']  # Only allow selection of member and book
        widgets = {
            'member': forms.Select(attrs={'class': 'form-control'}),
            'book': forms.Select(attrs={'class': 'form-control'}),
        }

class signupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['password1', 'password2']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


        