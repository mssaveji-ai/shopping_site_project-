from rest_framework import serializers
from .models import ProductGallery, Products, ProductCategory, ProductBrands, ProductReview, Wishlist

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id','title']

class ProductBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrands
        fields = ["id", "title"]

class ProductGallerySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = ProductGallery
        fields = ['image']
    
    def get_image(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url


class ProductSerializer(serializers.ModelSerializer):
    category = ProductCategorySerializer(many=True, read_only=True)
    brand = ProductBrandSerializer(read_only=True)

    class Meta:
        model = Products
        fields = ["id", "title","image","main_price","discount_price","short_description",
                 "category", "brand", "is_delete","stock"]
        

class ProductDetailSerializer(serializers.ModelSerializer):
    gallery = serializers.SerializerMethodField()
    views_count = serializers.IntegerField(read_only=True)
    category = ProductCategorySerializer(many=True, read_only=True)
    brand = ProductBrandSerializer(read_only=True)
    
    class Meta:
        model = Products
        fields = ["id", "title","image","gallery","main_price","discount_price","short_description",
                 "category","brand","views_count", "is_delete","stock"]
    
    def get_gallery(self, obj):
        gallery = ProductGallerySerializer(obj.gallery.all(), many=True, context=self.context).data
        request = self.context.get('request')

        if obj.image:
            main_image = request.build_absolute_uri(obj.image.url) if request else obj.image.url
            gallery.append({ 'image' : main_image})
        
        return gallery

    
class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['product', 'rating', 'text']
        read_only_fields = ['product']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                'Rating must be between 1 and 5'
            )
        return value
    
class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'created_at']
        read_only_fields = ['id', 'created_at']

    