from rest_framework import serializers
from .models import Book,Review


class BookSerializer(serializers.ModelSerializer):
    title = serializers.CharField(read_only=True)
    class Meta:
        model = Book
        fields =  ['id','title','author','publisher','summary','category']

class ReviewSerializer(serializers.ModelSerializer):
    book = BookSerializer()
    class Meta:
        model = Review
        fields = ['id','rating','comment','publication_date','book']