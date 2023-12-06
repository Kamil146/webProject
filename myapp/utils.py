import requests
from .models import Category
def get_book_info(isbn):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": f"isbn:{isbn}"}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "items" in data and data["items"]:
            book_info = data["items"][0]
            return book_info
        else:
            return None
    else:
        return None

def get_books_list(filter,type, max_results,sort_by="relevance"):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"{type}:{filter}",
        "maxResults": min(int(max_results),40),
        "orderBy": sort_by
    }
    response = requests.get(base_url, params=params)
    isbn = None
    if response.status_code == 200:
        data = response.json()
        if "items" in data and data["items"]:
            books_info = []
            for book in data["items"]:
                for identifier in book["volumeInfo"].get("industryIdentifiers", []):
                    if identifier.get("type") == "ISBN_13":
                        isbn = identifier.get("identifier", "")
                        break
                book_info = {
                    "isbn": isbn,
                    "author": ", ".join(book["volumeInfo"].get("authors", [])),
                    "title": book["volumeInfo"].get("title", ""),
                    "publisher": book["volumeInfo"].get("publisher", ""),
                    "publishedDate": book["volumeInfo"].get("publishedDate", ""),
                    "description": book["volumeInfo"].get("description", ""),
                    "categories" : book["volumeInfo"].get("categories", []),
                    "averageRating": book["volumeInfo"].get("averageRating", None)

                }
                books_info.append(book_info)
            return books_info
        else:
            return None
    else:
        return None

def get_book_rating(isbn,book):
    openlibrary_url = f"https://openlibrary.org/isbn/{isbn}.json"
    response = requests.get(openlibrary_url)
    data = response.json()
    if 'works' in data and data['works']:
        work_key = data['works'][0]['key']
    else:
        return None
    openlibrary_url_work_url  = f"https://openlibrary.org/{work_key}/ratings.json"
    response = requests.get(openlibrary_url_work_url)
    data = response.json()
    if data["summary"]["average"] is not None:
        openlibrary_average_value = round(data["summary"]["average"],1)
        openlibrary_count = round(data["summary"]["count"],1)
    else:
        openlibrary_average_value = 0
        openlibrary_count = 0

    google_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(google_url)
    data = response.json()
    volume_info = data["items"][0]['volumeInfo']
    google_average_value = volume_info.get('averageRating',0)
    google_count = volume_info.get('ratingsCount',0)
    weighted_values =openlibrary_average_value*openlibrary_count+google_average_value*google_count+book.average_rating*book.review_set.count()
    weighted_count = openlibrary_count+google_count+book.review_set.count()
    all_average = round(weighted_values/weighted_count,2)
    json_variable = {
        "book_info": {
            "name": book.title,
            "author" : book.author,
            "isbn" : book.isbn,},
        "ratings_openlibrary": {
                "average": openlibrary_average_value,
                "count": openlibrary_count},
        "ratings_googlebooks": {
                "average": google_average_value,
                "count": google_count},
        "ratings_mysite": {
                "average": book.average_rating,
                "count" : book.review_set.count(),},
            "all_average" : all_average}
    return json_variable


def create_or_get_categories(category_names):
    categories = []

    for category_name in category_names:
        # Sprawdź, czy kategoria już istnieje
        category, created = Category.objects.get_or_create(name=category_name)
        categories.append(category)

    return categories