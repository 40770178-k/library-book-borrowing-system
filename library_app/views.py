from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

from .forms import BookForm, MemberForm, BorrowedBookForm, signupForm
from .models import BorrowedBook, Book, Member

# Home Page
@login_required
def home(request):
    return render(request, 'home.html')

# Add Book
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_book')
    else:
        form = BookForm()
    return render(request, 'add_book.html', {'form': form})

# Add Member
def add_member(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_book')
    else:
        form = MemberForm()
    return render(request, 'add_member.html', {'form': form})

# Add Borrowed Book
def add_BorrowedBook(request):
    if request.method == 'POST':
        form = BorrowedBookForm(request.POST)
        if form.is_valid():
            borrowed_book = form.save(commit=False)
            book = borrowed_book.book

            if book.available_copies < 1:
                messages.error(request, f"No copies of '{book.title}' are available for borrowing.")
                return redirect('add_BorrowedBook')

            book.available_copies -= 1
            book.save()

            borrowed_book.save()
            messages.success(request, f"You have successfully borrowed '{book.title}'.")
            return redirect('add_BorrowedBook')
    else:
        form = BorrowedBookForm()
    return render(request, 'add_BorrowedBook.html', {'form': form})

# Return Borrowed Book
@require_POST
@login_required
def return_book(request, borrowed_book_id):
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        return redirect('signup')

    borrowed_book = get_object_or_404(BorrowedBook, id=borrowed_book_id)

    if borrowed_book.member != member:
        messages.error(request, "You can only return books borrowed by you.")
        return redirect('borrowed_books_list')

    if not borrowed_book.is_returned:
        borrowed_book.is_returned = True
        borrowed_book.returndate = timezone.now()
        borrowed_book.book.available_copies += 1
        borrowed_book.book.save()
        borrowed_book.save()
        messages.success(request, f"Book '{borrowed_book.book.title}' returned successfully.")
    else:
        messages.error(request, "This book has already been returned.")

    return redirect('borrowed_books_list')

# Borrowed Books List
def borrowed_books_list(request):
    borrowed_books = BorrowedBook.objects.select_related('member', 'book').filter(is_returned=False).order_by('-borrowdate')
    if not borrowed_books:
        messages.info(request, "No borrowed books found.")
    return render(request, 'borrowed_books_list.html', {'borrowed_books': borrowed_books, 'now': timezone.now()})

# Mark Book as Returned (Admin)
def mark_as_returned(request, pk):
    borrowed = get_object_or_404(BorrowedBook, pk=pk)
    if not borrowed.returned:
        borrowed.returned = True
        borrowed.returndate = timezone.now()
        borrowed.book.available_copies += 1
        borrowed.book.save()
        borrowed.save()
    return redirect('borrowed_books_list')

# User Login
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')  # Prevent loop if already logged in

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get('next', 'home'))  # To home or intended page
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

# Signup
def signup(request):
    if request.user.is_authenticated:
        return redirect('home')  # If already logged in, go to home

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')  # After signup, go to login
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})
