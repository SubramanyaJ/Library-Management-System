from django.contrib import admin
from .models import (
    LibraryUser,
    BookMain,
    AvailBooks,
    UserBorrowed,
    LateFees,
    Request,
    Rating,
    UserHistory
)


class LibraryUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'lib_num', 'is_active', 'fav_genre')
    search_fields = ('user__username', 'lib_num')
    list_filter = ('is_active',)
    ordering = ('user',)
    readonly_fields = ('lib_num',)

    fieldsets = (
        (None, {
            'fields': ('user', 'lib_num', 'is_active', 'fav_genre')
        }),
    )


admin.site.register(LibraryUser, LibraryUserAdmin)


class BookMainAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'title', 'author', 'genre', 'cover_image', 'average_rating')
    search_fields = ('isbn', 'title', 'author')
    list_filter = ('genre',)
    ordering = ('title',)

    def average_rating(self, obj):
        return obj.average_rating
    average_rating.short_description = 'Average Rating'


admin.site.register(BookMain, BookMainAdmin)


class AvailBooksAdmin(admin.ModelAdmin):
    list_display = ('book', 'total_books', 'available_books', 'books_borrowed', 'earliest_return')
    search_fields = ('book__title',)
    list_filter = ('book__genre',)

    def books_borrowed(self, obj):
        return obj.remaining_books

    books_borrowed.short_description = 'Books Borrowed'

    def earliest_return(self, obj):
        return obj.earliest_return()

    earliest_return.short_description = 'Earliest Return'


admin.site.register(AvailBooks, AvailBooksAdmin)


class UserBorrowedAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrow_date','return_date')
    search_fields = ('user__lib_num', 'book__book__title')
    list_filter = ('borrow_date',)
    ordering = ('-borrow_date',)


admin.site.register(UserBorrowed, UserBorrowedAdmin)


class UserHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'borrow_date', 'return_date', 'on_time')
    search_fields = ('user__lib_num', 'book__title')
    list_filter = ('on_time', 'return_date')
    ordering = ('-return_date',)


admin.site.register(UserHistory, UserHistoryAdmin)


class LateFeesAdmin(admin.ModelAdmin):
    list_display = ('user_borrowed', 'days_late', 'fee')
    search_fields = ('user_borrowed__user__lib_num',)
    list_filter = ('days_late',)


admin.site.register(LateFees, LateFeesAdmin)


class RequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'isbn', 'title', 'author', 'request_date')
    search_fields = ('isbn', 'title', 'user__lib_num')
    list_filter = ('request_date',)


admin.site.register(Request, RequestAdmin)


class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'rating', 'review', 'created_at')
    search_fields = ('user__lib_num', 'book__title')
    list_filter = ('rating', 'created_at')


admin.site.register(Rating, RatingAdmin)