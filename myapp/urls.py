
from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    path('books/', views.books_list),
    path('books/search/', views.search_book),
    path('reviews/',views.review_list),
    path('book/<int:id>',views.book_detail),
    path('review/<int:id>',views.review_detail),
    path('register',views.register_user),
    path('login',views.login_user),
    path('logout',views.logout_user),
    path('category',views.category_list),
]