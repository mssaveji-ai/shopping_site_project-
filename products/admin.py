from django.contrib import admin
from . import models

@admin.register(models.Products)
class ProductAdmin(admin.ModelAdmin):
    filter_horizontal = ['category', 'likes']

admin.site.register(models.ProductBrands)
admin.site.register(models.ProductCategory)
admin.site.register(models.ProductGallery)
admin.site.register(models.ProductVisit)
admin.site.register(models.ProductReview)
admin.site.register(models.Wishlist)
# Register your models here.
