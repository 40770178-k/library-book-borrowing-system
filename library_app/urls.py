from django.urls import include, path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('',views.user_login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('add-book/',views.add_book,name='add_book'),
    path('add-member/',views.add_member,name='add_member'),
    path('add-BorrowedBook/',views.add_BorrowedBook,name='add_BorrowedBook'),
    path('borrowed-books/',views.borrowed_books_list, name='borrowed_books_list'),
    path('return-book/<int:borrowed_book_id>/', views.return_book, name='return_book'),
    path('return-book/<int:pk>/', views.mark_as_returned, name='mark_as_returned'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]