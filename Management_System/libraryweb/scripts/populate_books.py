import os
import requests
from django.core.files import File
from io import BytesIO
from libraryweb.models import BookMain  # Replace 'yourapp' with your app name

# Open Library API base URLs
SEARCH_URL = "https://openlibrary.org/search.json"
COVER_URL = "https://covers.openlibrary.org/b/id/{}.jpg"

# Helper function to download and save an image
def download_image(cover_id):
    try:
        response = requests.get(COVER_URL.format(cover_id))
        if response.status_code == 200:
            return BytesIO(response.content)
    except Exception as e:
        print(f"Error downloading image: {e}")
    return None

# Fetch books data from Open Library
def fetch_books(query, limit=100):
    response = requests.get(SEARCH_URL, params={"q": query, "limit": limit})
    if response.status_code == 200:
        return response.json().get("docs", [])
    else:
        print("Failed to fetch books data.")
        return []

# Populate the database  

def populate_books():
    # Search terms for fetching different genres
    search_terms = [ "science", "mystery", "fantasy", "romance"]
    
    for term in search_terms:
        books = fetch_books(term, limit=100)  # Fetch 20 books per term
        for book_data in books:
            # Extract required details
            isbn = book_data.get("isbn", [None])[0]
            title = book_data.get("title")
            author = ", ".join(book_data.get("author_name", []))
            genre = term.title()  # Use the search term as genre
            cover_id = book_data.get("cover_i")

            # Skip if mandatory fields are missing
            if not (isbn and title and author and cover_id):
                continue

            # Check if the book with this ISBN already exists
            if BookMain.objects.filter(isbn=isbn).exists():
                print(f"Skipping duplicate ISBN: {isbn} - {title}")
                continue

            # Download cover image
            image_file = download_image(cover_id)
            if not image_file:
                continue

            # Create and save the book instance
            book = BookMain(
                isbn=isbn,
                title=title,
                author=author,
                genre=genre
            )
            book.cover_image.save(f"{isbn}.jpg", File(image_file), save=False)
            book.save()
            print(f"Added book: {title}")

populate_books()