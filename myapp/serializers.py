from rest_framework import serializers
from .models import Book, Review, User

class BookSerializerSmall(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'author']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'publisher', 'summary', 'category']


class ReviewSerializer(serializers.ModelSerializer):
    book = BookSerializer()

    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'publication_date', 'book','user']



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data['password']
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class ReviewSerializerSmall(serializers.ModelSerializer):
    book = BookSerializerSmall()
    user = UserSerializer()
    class Meta:
        model = Review
        fields = [ 'rating', 'book','user']