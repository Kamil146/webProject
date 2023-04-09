from django.shortcuts import render
from django.http import JsonResponse
from .models import Book,Review
from .serializers import BookSerializer,ReviewSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
# Create your views here.

@api_view(['GET', 'POST'])
def books_list(request,format=None):
    if request.method == 'GET':
        books = Book.objects.all()
        serializer =  BookSerializer(books, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer=BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

@api_view(['GET', 'POST'])
def review_list(request,format=None):
    if request.method == 'GET':
        reviews = Review.objects.all()
        serializer =  BookSerializer(reviews, many=True)
        return Response(serializer.data)
    if request.method == 'POST':
        serializer=ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)

@api_view(['GET','PUT','DELETE'])
def book_detail(request,id,format=None):
    try:
        book = Book.objects.get(pk=id)
    except Book.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method =='GET':
        serializer=BookSerializer(book)
        return Response(serializer.data)
    elif request.method =='PUT':
        serializer=BookSerializer(book,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    elif request.method =='DELETE':
        book.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET','PUT','DELETE','POST'])
def review_detail(request,id,format=None):

        try:
            review = Review.objects.get(pk=id)
        except Review.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            serializer = ReviewSerializer(review)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = ReviewSerializer(review, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            review.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif request.method == 'POST':
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)