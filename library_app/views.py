from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect,get_object_or_404
from .forms import BookForm,MemberForm,BorrowedBookForm
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import messages
from .models import BorrowedBook, Book, Member
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from .models import BorrowedBook, Member
from .forms import BorrowedBookForm
from django.contrib.auth.forms import AuthenticationForm

# Create your views here.
def home (request):
    return render(request,'home.html')

def add_book (request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_book')#reload the page or redirect to a success page
        
    else:
            form = BookForm()
            
    return render(request,'add_book.html',{'form': form})
        
def add_member (request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_book')#reload the page or redirect to a success page
        
    else:
            form = MemberForm()
            
    return render(request,'add_member.html',{'form': form})
        


def add_BorrowedBook(request):
    if request.method == 'POST':
        form = BorrowedBookForm(request.POST)
        if form.is_valid():
            borrowed_book = form.save(commit=False)

            # Optional: Update available_copies (if logic is needed)
            borrowed_book.book.available_copies -= 1
            borrowed_book.book.save()

            borrowed_book.save()
            return redirect('add_BorrowedBook')  # Reload the same page
    else:
        form = BorrowedBookForm()

    return render(request, 'add_BorrowedBook.html', {'form': form})

@login_required
def return_book(request, borrowed_book_id):
    member = Member.objects.get(email=request.user.email)
    borrowed_book = get_object_or_404(BorrowedBook, id=borrowed_book_id)

    if borrowed_book.member != member:
        messages.error(request, "You can only return books borrowed by you.")
        return redirect('borrowed_books_list')

    if not borrowed_book.is_returned:
        borrowed_book.is_returned = True
        borrowed_book.returndate = timezone.now()
        borrowed_book.save()
        messages.success(request, f"Book '{borrowed_book.book.title}' returned successfully.")
    else:
        messages.error(request, "This book has already been returned.")
    
    return redirect('add_BorrowedBook')


def borrowed_books_list(request):
     borrowed_books = BorrowedBook.objects.select_related('member', 'book')
     if not borrowed_books:
         messages.info(request, "No borrowed books found.")
     return render(request,'borrowed_books_list.html', {'borrowed_books': borrowed_books, 'now': timezone.now()})


def mark_as_returned(request, pk):
    borrowed=get_object_or_404(BorrowedBook, pk=pk)

    if not borrowed.returned:
         borrowed.returned = True
         borrowed.returndate = timezone.now() 
         borrowed.book.available_copies += 1
         borrowed.book.save()
         borrowed.save()
    
    return redirect('borrowed_books_list')

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next') or 'home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
