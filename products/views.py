from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from . models import ProductVisit, Products, ProductGallery, ProductReview, Wishlist
from utiles.get_ip import get_ip
from rest_framework import viewsets, status
from .serializers import ProductSerializer,ProductDetailSerializer, ProductReviewSerializer, WishlistSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .pagination import ProductPagination
from django.db.models import Q, Count
from django.db.models.functions import Coalesce
from basket.models import OrderDetail


class ProductDetail(DetailView):
    template_name = 'products/products_detail.html'
    model = Products
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        showed_product = self.object
        gallery = list(ProductGallery.objects.filter(product__id = showed_product.id))
        main_image = ProductGallery(image=showed_product.image)
        gallery.insert(0, main_image)
        context['gallery'] = gallery
        user_ip = get_ip(self.request)
        user = self.request.user
        if user.is_authenticated:
            has_been_visited = ProductVisit.objects.filter(product_id=showed_product.id, user=user).exists()
            # اگر که قبلا فردی ناشناس با این آی پی ویزیت کرده باید ویزیت جدید را حساب نکنیم
        else:
            has_been_visited = ProductVisit.objects.filter(product_id=showed_product.id, ip=user_ip).exists()
        if not has_been_visited:
            ProductVisit.objects.create(product=showed_product,ip=user_ip, user=user if user.is_authenticated else None)

        return context
    
    def get_queryset(self):
        query = super(ProductDetail,self).get_queryset()
        query = query.filter(is_delete = False)
        return query


class ProductDetailViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    queryset = Products.objects.select_related('brand').prefetch_related('category', 'gallery').filter(is_delete=False).annotate(views_count=Count('visits', distinct=True))
    
    def retrieve(self, request, pk):
        showed_product = get_object_or_404(self.get_queryset(), pk=pk)
        user_ip = get_ip(self.request)
        user = request.user
        if user.is_authenticated:
            has_been_visited = ProductVisit.objects.filter(product_id=showed_product.id, user=user).exists()
        else:
            has_been_visited = ProductVisit.objects.filter(product_id=showed_product.id, ip=user_ip).exists()
        if not has_been_visited:
            ProductVisit.objects.create(product=showed_product,ip=user_ip, user=user if user.is_authenticated else None)
        srz_data = self.get_serializer(showed_product)
        return Response(srz_data.data)

    
class ProductsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = ProductPagination

    def get_queryset(self):
        products = Products.objects.select_related('brand').prefetch_related('category').filter(is_delete=False).annotate(
            total_likes= Count('likes', distinct=True),
            final_price= Coalesce('discount_price', 'main_price'))

        category = self.kwargs.get('cat')
        if category:
            products = products.filter(category__slug=category)

        brand = self.kwargs.get('brand')
        if brand:
            products = products.filter(brand__slug=brand)

        stock = self.request.GET.get('stock')
        if stock == 'True':
            products = products.filter(stock__gt=0)
        elif stock == 'False':
            products = products.filter(stock=0)

        search = self.request.GET.get('q')
        if search:
            words = search.split()
        
            for word in words:
                products = products.filter(
                    Q(title__icontains=word) |
                    Q(category__title__icontains=word)|
                    Q(brand__title__icontains=word)|
                    Q(short_description__icontains=word)|
                    Q(main_description__icontains=word)
                    )
            products = products.distinct()

        sort = self.request.GET.get('sort')
        if sort == 'cheap':
            products = products.order_by("final_price")
        
        elif sort == 'expensive':
            products = products.order_by("-final_price")
        
        elif sort == "new":
            products = products.order_by("-created_at")
        
        elif sort == "popular":
            products = products.order_by("-total_likes")
        
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            products = products.filter(final_price__gte=min_price)
        if max_price:
            products = products.filter(final_price__lte=max_price)

        return products


@api_view(["POST"])

def like_product(request, pk):

    product = get_object_or_404(Products, pk=pk, is_delete=False)
    user = request.user
    liked = False

    if user in product.likes.all():
        product.likes.remove(user)
    else:
        product.likes.add(user)
        liked = True
    return Response({'liked': liked, 'status': 'ok'})


class ReviewAPI(APIView):

    def post(self, request):
        product_id = request.data.get('product')

        if not product_id:
            return Response(
                {'status': 'Product is required'},
                status=status.HTTP_400_BAD_REQUEST
    )
        product = get_object_or_404(
            Products,
            id=product_id,
            is_delete=False
        )

        has_bought = OrderDetail.objects.filter(order__user=request.user, order__is_paid=True, product_id=product_id).exists()

        if not has_bought:
            return Response({
                'status':'You can only review products you have purchased'
            }, status=status.HTTP_400_BAD_REQUEST)

        has_reviewed = ProductReview.objects.filter(user=request.user, product_id=product_id).exists()

        if has_reviewed:
            return Response({
                'status':'You can only review one time'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductReviewSerializer(data= request.data)

        if serializer.is_valid():
            serializer.save(user=request.user, product=product)

            return Response({
                'status':'Review created successfully'
            }, status=status.HTTP_201_CREATED)
        
        return Response (
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class ProductReviewListAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        product = get_object_or_404(Products, id=product_id, is_delete=False)
        reviews = ProductReview.objects.filter(product=product).order_by('-created_at')
        serializer = ProductReviewSerializer(reviews, many=True)

        return Response(serializer.data)


class UpdateReviewAPI(APIView):
    def patch(self, request, review_id):
        review = get_object_or_404(ProductReview, user=request.user, id=review_id)
        
        serializer = ProductReviewSerializer(review, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response({
                'status':'Review updated successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)

class DeleteReview(APIView):
    def delete(self, request, review_id):
        review = get_object_or_404(ProductReview, user=request.user, id=review_id)
        review.delete()

        return Response({
                'status':'Review deleted successfully'
            }, status=status.HTTP_200_OK)
    

class AddWishList(APIView):
    def post(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({
                'status':'Product_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        product = get_object_or_404(Products, id=product_id, is_delete=False)

        wished_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

        if not created:
            return Response({
                'status':'Product already exists in wishlist'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = WishlistSerializer(wished_item)
        return Response({
                'status':'Product added to wishlist',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

class WishlistAPI(APIView):
    def get(self, request):
        wishlist = Wishlist.objects.filter(user=request.user)

        serializer = WishlistSerializer(wishlist, many=True)

        return Response(serializer.data)
                

class RemoveWishList(APIView):
    def delete(self, request, product_id):
        wishlist_product = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
        wishlist_product.delete()

        return Response({
            "status":"Product removed from wishlist"
            },status=status.HTTP_200_OK)
