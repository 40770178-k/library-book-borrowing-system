from django import forms
from .models import Book,Member,BorrowedBook

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = '__all__'

class BorrowedBookForm(forms.ModelForm):
    class Meta:
        model = BorrowedBook
        fields = '__all__'