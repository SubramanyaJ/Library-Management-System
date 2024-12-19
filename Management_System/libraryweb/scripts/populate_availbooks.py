from libraryweb.models import BookMain, AvailBooks

# Loop through all BookMain entries
for book in BookMain.objects.all():
    # Create a corresponding AvailBooks entry for each BookMain record
    # Here, you can set the `total_books` and `available_books` to whatever initial values you prefer
    # For example, we set total_books to 10 and available_books to 10
    AvailBooks.objects.create(
        book=book,
        total_books=10,  # Set the number of total books (you can modify this as needed)
        available_books=10  # Set the available books (can be equal to total_books initially)
    )
    print(f"Populated AvailBooks for {book.title}")