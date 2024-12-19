from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator,MinValueValidator
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Avg
from django.contrib.auth.models import User


class LibraryUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="library_profile")
    lib_num = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=False)
    fav_genre = models.TextField(null=True, blank=True, help_text="Favorite genres, separated by commas.")  # New field

    def save(self, *args, **kwargs):
        if not self.lib_num:
            with transaction.atomic():
                current_year = now().year
                # Find the last LibraryUser lib_num of the current year
                last_user = LibraryUser.objects.filter(lib_num__startswith=f"{current_year}LIB").order_by('-lib_num').first()
                if last_user:
                    last_number = int(last_user.lib_num[8:]) + 1  # Extract the numeric part
                else:
                    last_number = 1
                self.lib_num = f"{current_year}LIB{last_number:04d}"  # Format: YYYYLIB0001
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.lib_num})"


class BookMain(models.Model):
    id = models.AutoField(primary_key=True)
    isbn = models.CharField(max_length=13, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=50)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)

    @property
    def average_rating(self):
        return self.ratings.aggregate(average=Avg('rating'))['average'] or 0

    def __str__(self):
        return self.title


class AvailBooks(models.Model):
    book = models.OneToOneField(BookMain, on_delete=models.CASCADE, related_name="availability")
    total_books = models.PositiveIntegerField(default=0)
    available_books = models.PositiveIntegerField(default=0)

    @property
    def remaining_books(self):#Borrowed Books
        return self.total_books - self.available_books

    def earliest_return(self):
        if self.total_books == self.available_books:
            return None  # All books are available
        
        earliest_borrow = self.borrowed_instances.order_by('borrow_date').first()
        if earliest_borrow:
            return earliest_borrow.borrow_date + timedelta(days=3)
        return None  # No borrowed books
    
    def clean(self):
        # Check if available_books is greater than total_books
        if self.available_books > self.total_books:
            raise ValidationError(f"Available books cannot be greater than total books for '{self.book.title}'.")

    def __str__(self):
        return f"{self.book.title}: {self.available_books}/{self.total_books}"


class UserHistory(models.Model):
    user = models.ForeignKey(LibraryUser, on_delete=models.CASCADE, related_name="borrow_history")
    book = models.ForeignKey(BookMain, on_delete=models.CASCADE, related_name="borrow_history")
    borrow_date = models.DateTimeField()
    return_date = models.DateTimeField(auto_now_add=True)
    on_time = models.BooleanField()

    def save(self, *args, **kwargs):
        due_date = self.borrow_date + timedelta(days=3)
        self.on_time = self.return_date <= due_date
        super().save(*args, **kwargs)

    def __str__(self):
        return f"History: {self.user.lib_num} returned {self.book.title} - {'On Time' if self.on_time else 'Late'}"


class UserBorrowed(models.Model):
    user = models.ForeignKey(LibraryUser, on_delete=models.CASCADE, related_name="borrowed_books")
    book = models.ForeignKey(AvailBooks, on_delete=models.CASCADE, related_name="borrowed_instances")
    borrow_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.book.available_books -= 1
        self.book.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            # Increment the available books count
            self.book.available_books += 1
            self.book.save()
        super().delete(*args, **kwargs)
    
    def clean(self):
        # Check if available_books is greater than total_books
        if self.user.borrowed_books.count() >= 3:
            raise ValidationError("A user can only borrow a maximum of 3 books at a time.")
        if self.book.available_books == 0:
            raise ValidationError("Book is not available for borrowing.")
        

    @property
    def return_date(self):
        """Calculate the return date as 7 days after the borrow date."""
        return self.borrow_date + timedelta(days=3)

    def __str__(self):
        return f"{self.user.lib_num} Borrowed {self.book.book.title} on {self.borrow_date.day}/{self.borrow_date.month}/{self.borrow_date.year}"

class LateFees(models.Model):
    user_borrowed = models.OneToOneField(UserBorrowed, on_delete=models.CASCADE, related_name="late_fee")
    days_late = models.PositiveIntegerField(default=0)
    fee = models.PositiveIntegerField(default=0)

    def calculate_fees(self):
        due_date = self.user_borrowed.borrow_date + timedelta(days=3)
        if now() > due_date:
            self.days_late = (now() - due_date).days
            self.fee = self.days_late * 50  # ₹50 per day late
        else:
            self.days_late = 0
            self.fee = 0
        self.save()

    def __str__(self):
        return f"Late Fee for {self.user_borrowed.user.lib_num}: ₹{self.fee}"


class Request(models.Model):
    user = models.ForeignKey(LibraryUser, on_delete=models.CASCADE, related_name="book_requests")
    isbn = models.CharField(max_length=13)
    title = models.CharField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=255, blank=True, null=True)
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.lib_num} requested {self.title or 'unknown book'}"


class Rating(models.Model):
    user = models.ForeignKey(LibraryUser, on_delete=models.CASCADE, related_name="ratings")  # Related to LibraryUser
    book = models.ForeignKey(BookMain, on_delete=models.CASCADE, related_name="ratings")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)])  # 0-5 scale
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')  # Each user can review a book only once

    def __str__(self):
        return f"{self.user.lib_num} rated {self.book.title} - {self.rating}"