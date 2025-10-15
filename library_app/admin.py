from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'book')
    search_fields = ('book__title', 'member__fullname', 'comment')
from .models import Book,Member,BorrowedBook

# Register your models here.
admin.site.register(Book)
admin.site.register(Member)
admin.site.register(BorrowedBook)

