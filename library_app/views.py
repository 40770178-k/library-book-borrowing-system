from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from .forms import BookForm, MemberForm, BorrowedBookForm, signupForm
from .models import BorrowedBook, Book, Member
from functools import wraps
from .forms import signupForm

def member_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        try:
            request.member = Member.objects.get(user=request.user)
        except Member.DoesNotExist:
            messages.error(request, "You need to create a member profile first.")
            return redirect('add_member')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Home Page
@login_required
def home(request):
    return render(request, 'home.html')

# Add Book
@login_required
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
@login_required
@member_required
def add_BorrowedBook(request):
    member = request.member
    if request.method == 'POST':
        form = BorrowedBookForm(request.POST)
        if form.is_valid():
            borrowed_book = form.save(commit=False)
            book = borrowed_book.book

            if book.available_copies < 1:
                messages.error(request, f"No copies of '{book.title}' are available for borrowing.")
                return redirect('add_BorrowedBook')

            # Set the user field to the current user
            borrowed_book.user = request.user
            
            # Ensure is_returned is False
            borrowed_book.is_returned = False
            
            # Reduce available copies
            book.available_copies -= 1
            book.save()

            # Save the borrowed book
            borrowed_book.save()
            
            # Debug: Print to console
            print(f"Book borrowed: {borrowed_book.book.title} by {borrowed_book.member.fullname}")
            print(f"Is returned: {borrowed_book.is_returned}")
            print(f"User: {borrowed_book.user}")
            
            messages.success(request, f"You have successfully borrowed '{book.title}'.")
            return redirect('add_BorrowedBook')
    else:
        form = BorrowedBookForm()
    return render(request, 'add_BorrowedBook.html', {'form': form})

# Return Borrowed Book
@require_POST
@login_required
@member_required
def return_book(request, borrowed_book_id):
    member = request.member
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
@login_required
@member_required
def borrowed_books_list(request):
    member = request.member
    # Debug: Print user info
    print(f"User: {request.user}")
    print(f"User is authenticated: {request.user.is_authenticated}")
    
    # Check if user has a member profile
    try:
        member = Member.objects.get(user=request.user)
        print(f"User's member profile: {member.fullname}")
    except Member.DoesNotExist:
        print("User does not have a member profile")
        messages.error(request, "You need to create a member profile first.")
        return redirect('add_member')
    
    # Get all borrowed books that are not returned
    borrowed_books = BorrowedBook.objects.select_related('member', 'book').filter(is_returned=False).order_by('-borrowdate')
    
    # Debug: Print count to console
    print(f"Found {borrowed_books.count()} borrowed books")
    
    # Debug: Print all borrowed books details<a class="nav-link" href="{% url 'admin_dashboard' %}">Admin Dashboard</a>
    for book in borrowed_books:
        print(f"Book: {book.book.title}, Member: {book.member.fullname}, Is returned: {book.is_returned}")
    
    if not borrowed_books:
        messages.info(request, "No borrowed books found.")
    
    return render(request, 'borrowed_books_list.html', {'borrowed_books': borrowed_books, 'now': timezone.now()})

# Mark Book as Returned (Admin)
@staff_member_required
def mark_as_returned(request, pk):
    borrowed = get_object_or_404(BorrowedBook, pk=pk)
    if not borrowed.is_returned:
        borrowed.is_returned = True
        borrowed.returndate = timezone.now()
        borrowed.book.available_copies += 1
        borrowed.book.save()
        borrowed.save()
        messages.success(request, f"Book '{borrowed.book.title}' has been marked as returned by admin.")
    else:
        messages.error(request, "This book has already been returned.")
    return redirect('admin_dashboard')

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
            if not User.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request, "No account found with that username.")
                return redirect('signup')
            else:
                messages.error(request, "Invalid username or password.")
                return redirect('login')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

# Signup
def sync_username_with_fullname(user):
    try:
        member = Member.objects.get(user=user)
        user.username = member.fullname
        user.save()
    except Member.DoesNotExist:
        pass


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        user_form = signupForm(request.POST)
        member_form = MemberForm(request.POST)
        if user_form.is_valid() and member_form.is_valid():
            member = member_form.save(commit=False)
            user = user_form.save(commit=False)
            user.username = member.fullname  # Set username to full name
            user.save()
            member.user = user
            member.save()
            login(request, user)
            messages.success(request, "Signup successful!")
            return redirect('home')
    else:
        user_form = signupForm()
        member_form = MemberForm()

    return render(request, 'signup.html', {
        'form': user_form,
        'member_form': member_form
    })

# Edit Member Profile (sync username with fullname)
@login_required
@member_required
def edit_member(request):
    member = request.member
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            member = form.save()
            user = member.user
            user.username = member.fullname
            user.save()
            messages.success(request, "Profile updated!")
            return redirect('home')
    else:
        form = MemberForm(instance=member)
    return render(request, 'edit_member.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

#admin dashboard
@staff_member_required
def admin_dashboard(request):
    filter_type = request.GET.get('filter')
    if filter_type == 'not_returned':
        borrowed_books = BorrowedBook.objects.select_related('member', 'book').filter(is_returned=False).order_by('-borrowdate')
    else:
        borrowed_books = BorrowedBook.objects.select_related('member', 'book').order_by('-borrowdate')
    
    # Debug: Print counts to console
    print(f"Admin dashboard - Total books: {borrowed_books.count()}")
    print(f"Admin dashboard - Not returned: {BorrowedBook.objects.filter(is_returned=False).count()}")
    
    # Debug: Print all books details
    for book in borrowed_books:
        print(f"Admin - Book: {book.book.title}, Member: {book.member.fullname}, Is returned: {book.is_returned}")
    
    if not borrowed_books:
        messages.info(request, "No borrowed books found.")
    return render(request, 'admin_dashboard.html', {'borrowed_books': borrowed_books, 'now': timezone.now(), 'filter_type': filter_type})


def available_books(request):
    books = Book.objects.filter(available_copies__gt=0).order_by('title')
    
    # Debug: Print available books count
    print(f"Available books count: {books.count()}")
    
    if not books:
        messages.info(request, "No available books found.")
    
    return render(request, 'available_books.html', {'books': books})

@login_required
def my_borrowed_books(request):
    user = request.user
    borrowed_books = BorrowedBook.objects.filter(user=user, is_returned=False).select_related('book').order_by('-borrowdate')
    
    # Debug: Print user's borrowed books count
    print(f"My borrowed books count: {borrowed_books.count()}")
    
    if not borrowed_books:
        messages.info(request, "You have no borrowed books.")
    
    return render(request, 'my_borrowed_books.html', {'borrowed_books': borrowed_books, 'now': timezone.now()})