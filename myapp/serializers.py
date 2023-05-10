from rest_framework import serializers
from .models import Book, Review, User, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class BookSerializerSmall(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id','title', 'author']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'publisher', 'summary', 'category']

# class ReviewSerializerAdd(serializers.ModelSerializer):
#     book_title = serializers.CharField(source='book.title', read_only=True)
#     user = serializers.HiddenField(default=serializers.CurrentUserDefault())
#     class Meta:
#         model = Review
#         fields = ['id', 'rating', 'comment', 'publication_date', 'book_title', 'user']

class ReviewSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    user_name =  serializers.CharField(source='user.username',read_only=True)
    class Meta:
        model = Review
        fields = ['id', 'rating', 'comment', 'publication_date', 'book_title','user_name']



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
    book_title = serializers.CharField(source='book.title',read_only=True)
    user_name =  serializers.CharField(source='user.username',read_only=True)
    class Meta:
        model = Review
        fields = [ 'id','rating', 'book_title','user_name']