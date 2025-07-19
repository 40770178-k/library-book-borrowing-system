from django.db import models
from django.core.validators import RegexValidator, MinValueValidator as minvalidator
from django.forms import ValidationError

# Create your models here.
class Book(models.Model):
    title=models.CharField(max_length=255)
    author=models.CharField(max_length=255)
    total_copies=models.PositiveIntegerField(validators=[minvalidator(0)], default=0)
    available_copies=models.PositiveIntegerField(validators=[minvalidator(0)], default=0)
    date_added=models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def clean(self):
        if self.total_copies < 0 or self.available_copies < 0:
            raise ValidationError('Copy values cannot be negative.')

class Member(models.Model):
    fullname=models.CharField(max_length=255)
    email=models.EmailField()
    phonenumber=models.CharField(max_length=13,validators=[RegexValidator(r'^\+?\d{10,13}$',message='Enter a valid phone number(10-13digits)')],)
    registration_date=models.DateField()
    
    def __str__(self):
        return self.fullname

class BorrowedBook(models.Model):
    member=models.ForeignKey(Member,on_delete=models.CASCADE)
    book=models.ForeignKey(Book,on_delete=models.CASCADE)
    borrowdate=models.DateField(auto_now_add=True)
    returndate=models.DateField(null=True, blank=True,auto_now_add=True)
    is_returned=models.BooleanField(default=False)
    def __str__(self):
        return f"{self.member.fullname} borrowed {self.book.title}"

