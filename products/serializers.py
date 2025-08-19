from rest_framework import serializers
from .models import ProductGallery, ProductVisit, Products, ProductCategory, ProductBrands

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id','title']

class ProductBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrands
        fields = ["id", "title"]

class ProductGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGallery
        fields = ['image']

class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(many=True, read_only=True)
    brand = ProductBrandSerializer(read_only=True)

    class Meta:
        model = Products
        fields = ["id", "title","image","main_price","discount_price","short_description","likes_count",
                 "category", "brand", "is_delete","in_stock"]
        

class ProductDetailSerializer(serializers.ModelSerializer):
    gallery = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    category = ProductCategorySerializer(many=True, read_only=True)
    brand = ProductBrandSerializer(read_only=True)
    
    class Meta:
        model = Products
        fields = ["id", "title","image","gallery","main_price","discount_price","short_description","likes_count",
                 "category","brand","views_count", "is_delete","in_stock"]
    
    def get_gallery(self, obj):
        gallery_query = ProductGallery.objects.filter(product=obj)
        srz_gallery = ProductGallerySerializer(gallery_query, many=True, context=self.context).data
        main_image = [{'image': obj.image.url}] if obj.image else []
        return srz_gallery + main_image
    
    def get_views_count(self, obj):
        return ProductVisit.objects.filter(product=obj).count()
    

