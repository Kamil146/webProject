from django.contrib import admin
from .models import Book,Category,Review,User
# Register your models here.
class BookAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
admin.site.register(Book,BookAdmin)

class CategoryAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
admin.site.register(Category,CategoryAdmin)

admin.site.register(User)

class ReviewAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'publication_date')
admin.site.register(Review, ReviewAdmin)