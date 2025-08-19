from tabnanny import verbose
from django.db import models
from django.utils.text import slugify
from accounts.models import User

class ProductCategory(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    slug = models.CharField(max_length=200, db_index=True,null=True,blank=True)
    is_delete = models.BooleanField(default=False)
    
    def save(self,*args,**kwargs):
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        while Products.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
        super().save(*args,**kwargs)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.title
    
class ProductBrands(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    slug = models.CharField(max_length=200, db_index=True,null=True,blank=True)
    is_delete = models.BooleanField(default=False)
    
    def save(self,*args,**kwargs):
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        while Products.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
        super().save(*args,**kwargs)
    
    class Meta:
        verbose_name_plural = "Brands"
    
    def __str__(self):
        return self.title
    
class Products(models.Model):
    title = models.CharField(max_length=300)
    category = models.ManyToManyField(ProductCategory,related_name='product_categories')
    brand = models.ForeignKey(ProductBrands, on_delete=models.CASCADE, null = True, blank= True, related_name='product_brand' )
    image = models.ImageField(upload_to='images/products', null=True, blank=True)
    main_price = models.IntegerField()
    discount_price = models.IntegerField(null=True, blank=True)
    short_description = models.CharField(max_length=300, null=True, blank=True, db_index=True)
    main_description = models.TextField(db_index= True)
    likes = models.ManyToManyField(User, related_name='product_like', null=True, blank=True)
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, null = True, db_index= True, blank= True,max_length= 200)
    in_stock = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    
    def likes_count(self):
        return self.likes.count()
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name_plural = "Products"
    
    def save(self,*args,**kwargs):
        base_slug = slugify(self.title)
        slug = base_slug
        counter = 1
        while Products.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug
        super().save(*args,**kwargs)

class ProductGallery(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/product_galley')

    def __str__(self):
        return self.product.title
    
    class Meta:
        verbose_name_plural = 'ProductGalleries'

class ProductVisit(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True )

    def __str__(self):
        return f"{self.product.title}-{self.ip}"

