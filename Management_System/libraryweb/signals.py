from django.db.models.signals import post_delete,pre_delete,post_save
from django.dispatch import receiver
from .models import UserHistory,UserBorrowed,LateFees
from django.utils.timezone import now
from datetime import timedelta

@receiver(post_delete, sender=UserBorrowed)
def create_user_history_on_delete(sender, instance, **kwargs):
    borrow_date = instance.borrow_date
    return_date = now()
    due_date = borrow_date + timedelta(days=3)
    on_time = return_date <= due_date

    UserHistory.objects.create(
        user=instance.user,
        book=instance.book.book,
        borrow_date=borrow_date,
        return_date=return_date,
        on_time=on_time
    )

@receiver(pre_delete, sender=UserBorrowed)
def handle_bulk_delete(sender, instance, **kwargs):
    # Increment the available_books count before deletion
    instance.book.available_books += 1
    instance.book.save()

@receiver(post_save, sender=UserBorrowed)
def create_late_fees(sender, instance, created, **kwargs):
    if created:
        LateFees.objects.create(user_borrowed=instance)