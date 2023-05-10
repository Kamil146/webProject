
from django.shortcuts import render
from django.http import JsonResponse
from .models import Book, Review, User, Category
from .serializers import CategorySerializer,BookSerializer, ReviewSerializer, UserSerializer, BookSerializerSmall, ReviewSerializerSmall
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.db.models import Q

@api_view(['POST'])
def login_user(request, format=None):
    password = request.data.get('password')
    username_or_email = request.data.get('login')
    # Sprawdzenie czy użytkownik istnieje w bazie danych
    user = None
    if username_or_email and '@' in username_or_email:

        user = User.objects.filter(email=username_or_email).first()
    elif username_or_email:

        user = User.objects.filter(username=username_or_email).first()

    # Jeśli użytkownik istnieje, sprawdź poprawność hasła
    if user and user.check_password(password):
        token = Token.objects.get_or_create(user=user)[0]
        response = Response({'message': 'Zalogowano pomyślnie'})
        response.set_cookie('auth_token', token.key)  # ustawienie ciasteczka
        response['Authorization'] =  'Token ' + token.key
        return response
    else:
        return Response({'error': 'Nieprawidłowy login lub hasło'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request, format=None):
    request.user.auth_token.delete()
    response = Response({'message': 'Wylogowano pomyślnie'})
    response.delete_cookie('auth_token')  # usuwanie ciasteczka
    return response

@api_view(['POST'])
def register_user(request, format=None):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def category_list(request,format=None):
    if request.method == 'GET':
        categories =  Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
@api_view(['GET', 'POST'])
def books_list(request, format=None):
    if request.method == 'GET':
        books = Book.objects.all()
        serializer = BookSerializerSmall(books, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def review_list(request, format=None):
    if request.method == 'GET':
        reviews = Review.objects.all()
        serializer = ReviewSerializerSmall(reviews, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        book_title = request.data.get('book_title')

        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            try:
                book = Book.objects.get(title=book_title)
            except Book.DoesNotExist:
                return Response({'error': 'Book does not exist'}, status=status.HTTP_404_NOT_FOUND)
            serializer.save(book=book)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET', 'PUT', 'DELETE','POST'])
def book_detail(request, id, format=None):
    try:
        book = Book.objects.get(pk=id)
    except Book.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BookSerializer(book)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'POST':
        existing_review = Review.objects.filter(book=id, user=request.user)
        if existing_review.exists():
            return Response({'error': 'User already reviewed this book.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ReviewSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            serializer.save(book=book, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def review_detail(request, id, format=None):
    try:
        review = Review.objects.get(pk=id)
    except Review.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    elif request.method == 'PUT':
        if review.user == request.user:
            serializer = ReviewSerializer(review, data=request.data,context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    elif request.method == 'DELETE':
        if review.user == request.user:
            review.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def search_book(request):
    queryset = Book.objects.all()
    query = request.query_params.get('query', '')
    if query:
        q = Q()
        for field in ['title', 'author']:
            q |= Q(**{f"{field}__icontains": query})
        queryset = queryset.filter(q)
    serializer = BookSerializerSmall(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)