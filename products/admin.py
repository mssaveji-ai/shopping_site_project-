from django.contrib import admin
from . import models

admin.site.register(models.Products)
admin.site.register(models.ProductBrands)
admin.site.register(models.ProductCategory)
admin.site.register(models.ProductGallery)
admin.site.register(models.ProductVisit)
# Register your models here.
