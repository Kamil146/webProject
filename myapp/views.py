from django.shortcuts import render
from django.http import JsonResponse
from .models import Book, Review, User, Category
from .serializers import CategorySerializer, BookSerializer, ReviewSerializer, UserSerializer, BookSerializerSmall, \
    ReviewSerializerSmall
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.db.models import Q
from .utils import get_book_info, get_books_list, get_book_rating, create_or_get_categories
from django.utils.html import strip_tags
from rest_framework import serializers
from django.contrib.auth import authenticate


@api_view(['GET'])
def create_book_from_isbn(request, isbn):
    # Utwórz URL zapytania do Google Books API
    if len(str(isbn)) != 13:
        return Response({"error": "Incorrent length of ISBN"}, status=status.HTTP_404_NOT_FOUND)
    books = Book.objects.all()
    books = books.filter(isbn=isbn).first()
    if books:
        return Response({"error": "Book with that ISBN already exists"}, status=status.HTTP_404_NOT_FOUND)
    data = get_book_info(isbn)
    # Sprawdź, czy zapytanie zwróciło wyniki
    if data is None:
        return Response({"error": "No results for that ISBN"}, status=status.HTTP_404_NOT_FOUND)
    # Pobierz informacje o pierwszym wyniku
    book_info = data['volumeInfo']
    summary = strip_tags(book_info.get('description', ''))
    category_names = book_info.get('categories', [])
    categories = create_or_get_categories(category_names)
    # Utwórz instancję modelu Book na podstawie informacji z API
    book_data = {
        'title': book_info.get('title', ''),
        'author': ', '.join(book_info.get('authors', [])),
        'publisher': book_info.get('publisher', ''),
        'isbn': isbn,
        'summary': summary,
        'category': categories,
        'average_rating': 0.0
    }
    # Utwórz nową książkę
    book_serializer = BookSerializer(data=book_data)
    if book_serializer.is_valid():
        book_serializer.save()
        return Response(book_serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(book_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def create_books_from_list(request):
    author = request.GET.get('author', '')
    category = request.GET.get('category', '')
    save = request.GET.get('save', '')
    max_results = request.GET.get('max', '3')
    # Pobierz informacje o książce z API Google Books
    if author:
        data = get_books_list(author, 'inauthor', max_results)
    elif category:
        data = get_books_list(category, 'subject', max_results)
    if save:
        if data:
            books_info = data
            # Przechodzimy przez listę książek
            for book_info in books_info:
                isbn = book_info.get('isbn', '')
                category_names = book_info.get('categories', [])
                categories = create_or_get_categories(category_names)
                # Utwórz instancję modelu Book na podstawie informacji z API
                book_data = {
                    'title': book_info.get('title', ''),
                    'author': book_info.get('author', ''),
                    'publisher': book_info.get('publisher', ''),
                    'isbn': isbn,
                    'summary': strip_tags(book_info.get('description', '')),
                    'category': categories,
                    'average_rating': 0.0
                }
                books = Book.objects.all()
                books = books.filter(isbn=isbn).first()
                if books:
                    pass
                # Utwórz nową książkę
                book_serializer = BookSerializer(data=book_data)
                if book_serializer.is_valid():
                    book_serializer.save()
                else:
                    pass
            return Response({"message": "Books added successfully"}, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({"error": "Could not access information about books"}, status=400)
    return Response(data)


@api_view(['GET'])
def book_ratings(request, id):
    try:
        book = Book.objects.get(pk=id)
    except Book.DoesNotExist:
        return JsonResponse({"error": "Book with that ID does not exist"}, status=404)
    # Sprawdź, czy książka ma przypisane ISBN
    if not book.isbn:
        return JsonResponse({"error": "Book does not have ISBN "}, status=400)
    # Pobierz informacje o książce z API Google Books
    books_rating = get_book_rating(book.isbn, book)

    if not books_rating:
        return JsonResponse({"error": "Could not access books information"}, status=400)

    return Response(books_rating)


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


@api_view(['POST'])
def login_user(request, format=None):
    # Utwórz instancję serializera na podstawie danych wejściowych
    serializer = LoginSerializer(data=request.data)

    # Sprawdź poprawność danych wejściowych
    if serializer.is_valid():
        username_or_email = serializer.validated_data['login']
        password = serializer.validated_data['password']

        user = None
        if '@' in username_or_email:
            user = User.objects.filter(email=username_or_email).first()
        else:
            user = User.objects.filter(username=username_or_email).first()

        if user:
            authenticated_user = authenticate(request, username=user.username, password=password)
            if authenticated_user:
                token, created = Token.objects.get_or_create(user=authenticated_user)
                response = Response({'message': f'Login successful {authenticated_user.username}'})
                response.set_cookie('auth_token', token.key)
                response['Authorization'] = 'Token ' + token.key
                return response
            else:
                return Response({'error': 'Incorrect password or user does not exist'})
        else:
            return Response({'error': 'User does not exist'})
    else:
        # Dane wejściowe nie są poprawne, zwróć błąd walidacji
        return Response({'error': serializer.errors})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request, format=None):
    request.user.auth_token.delete()
    response = Response({'message': 'Logout succesfull'})
    response.delete_cookie('auth_token')
    return response


@api_view(['POST'])
def register_user(request, format=None):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Register succesfull', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Register unsuccessful', 'errors': serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def category_list(request, format=None):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def books_list(request, format=None):
    if request.method == 'GET':
        books = Book.objects.all()
        # for book in books:
        #     book.update_average_rating()
        search = request.query_params.get('search', '')
        category = request.query_params.get('category', '')
        sort_by = request.query_params.get('sort_by', '')
        if search:
            title_q = Q(title__icontains=search)
            author_q = Q(author__icontains=search)
            books = books.filter(title_q | author_q)
        if category:
            books = books.filter(category__name__icontains=category)
        if sort_by:
            books = books.order_by(sort_by)

        serializer = BookSerializerSmall(books, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def review_list(request, format=None):
    if request.method == 'GET':
        reviews = Review.objects.all()
        user = request.query_params.get('user', '')
        title = request.query_params.get('title', '')
        sort_by = request.query_params.get('sort_by', '')
        if user:
            reviews = reviews.filter(user__username__icontains=user)
        if title:
            reviews = reviews.filter(book__title__icontains=title)
        if sort_by:
            reviews = reviews.order_by(sort_by)
        serializer = ReviewSerializerSmall(reviews, many=True)
        return Response(serializer.data)


@api_view(['GET', 'PUT', 'DELETE'])
def book_detail(request, id, format=None):
    try:
        book = Book.objects.get(pk=id)
        book.update_average_rating()
    except Book.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = BookSerializer(book)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if not request.user.groups.filter(name="bookadmin").exists():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if not request.user.groups.filter(name="bookadmin").exists():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE', 'POST'])
def review_detail(request, id, format=None):
    if request.method == 'POST':
        try:
            book = Book.objects.get(pk=id)
        except Book.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.user.is_authenticated:
            existing_review = Review.objects.filter(book=id, user=request.user)
            if existing_review.exists():
                return Response({'error': 'User already reviewed this book.'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(book=book, user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'User is not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)
    try:
        review = Review.objects.get(pk=id)
    except Review.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
    elif request.method == 'PUT':
        if review.user == request.user:
            serializer = ReviewSerializer(review, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'You can only modify your reviews'}, status=status.HTTP_401_UNAUTHORIZED, )
    elif request.method == 'DELETE':
        if review.user == request.user:
            review.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'You can only delete your reviews'}, status=status.HTTP_401_UNAUTHORIZED)
