from django.db import models
from django.core.validators import RegexValidator

# Create your models here.
class Book(models.Model):
    title=models.CharField(max_length=255)
    author=models.CharField(max_length=255)
    total_copies=models.IntegerField()
    available_copies=models.IntegerField(blank=True,null=True)
    date_added=models.DateField(auto_now_add=True)

class Member(models.Model):
    fullname=models.CharField(max_length=255)
    email=models.EmailField()
    phonenumber=models.CharField(max_length=13,validators=[RegexValidator(r'^\+?\d{10,13}$',message='Enter a valid phone number(10-13digits)')],)
    registration_date=models.DateField()

class BorrowedBook(models.Model):
    member=models.ForeignKey(Member,on_delete=models.CASCADE)
    book=models.ForeignKey(Book,on_delete=models.CASCADE)
    borrowdate=models.DateField(auto_now_add=True)
    returndate=models.DateField(null=True, blank=True)
    is_returned=models.BooleanField(default=False)
    def __str__(self):
        return f"{self.member.fullname} borrowed {self.book.title}"

