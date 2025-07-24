from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect,get_object_or_404
from .forms import BookForm,MemberForm,BorrowedBookForm, signupForm
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import messages
from .models import BorrowedBook, Book, Member
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from .models import BorrowedBook, Member
from .forms import BorrowedBookForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST

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

@require_POST
@login_required
def return_book(request, borrowed_book_id):
    try:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
        return redirect('signup')  # Redirect to signup if member does not exist

    borrowed_book = get_object_or_404(BorrowedBook, id=borrowed_book_id)

    if borrowed_book.member != member:
        messages.error(request, "You can only return books borrowed by you.")
        return redirect('borrowed_books_list')

    if request.method == 'POST':
        if not borrowed_book.is_returned:
            borrowed_book.is_returned = True
            borrowed_book.returndate = timezone.now()
            borrowed_book.save()
            messages.success(request, f"Book '{borrowed_book.book.title}' returned successfully.")
        else:
            messages.error(request, "This book has already been returned.")

        return redirect('add_BorrowedBook')

    return render(request, 'return_book.html', {'book': borrowed_book})



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

def signup(request):
 if request.method == 'POST':
     form= signupForm(request.POST)
     if form.is_valid():
         user= form.save(commit=False)
         user.set_password(form.cleaned_data['password'])
         user.save()
         Member.object.create(user=user)
         login(request, user)
         return redirect('home')
     else:
        form = signupForm()
     return render(request, 'signup.html', {'form': form})
 
 from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from .models import Member
from django.contrib import messages

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        phonenumber = request.POST['phone']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect('signup')

        user = User.objects.create_user(username=username, password=password)
        Member.objects.create(user=user, phonenumber=phonenumber)
        messages.success(request, 'Account created successfully. You can log in.')
        return redirect('login')  # or wherever your login URL is

    return render(request, 'signup.html')
