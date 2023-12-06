from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255,unique=True)
    password = models.CharField(max_length=255)
    username = models.CharField(max_length=255,unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100,blank=True)
    isbn = models.CharField(max_length=13,unique=True)
    summary = models.TextField(blank=True)
    category = models.ManyToManyField(Category)
    average_rating = models.FloatField(default=0.0)
    def __str__(self):
        return self.title

    def update_average_rating(self):
        total_ratings = self.review_set.count()
        if total_ratings > 0:
            sum_ratings = sum([review.rating for review in self.review_set.all()])
            self.average_rating = sum_ratings / total_ratings
        else:
            self.average_rating = 0.0
        self.save()

class Review(models.Model):
    RATING_OPTIONS=((1,1),(2,2),(3,3),(4,4),(5,5),(6,6))
    rating = models.IntegerField(choices=RATING_OPTIONS)
    comment = models.TextField()
    publication_date = models.DateField('published on:', auto_now=True)
    book = models.ForeignKey(Book,on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.book.title + ' book review'