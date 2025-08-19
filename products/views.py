from django.shortcuts import get_object_or_404, render,redirect
from django.views.generic import ListView, DetailView
from . models import ProductVisit, Products, ProductGallery, ProductCategory,ProductBrands
from django.core.files.images import ImageFile
from utiles.get_ip import get_ip
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from rest_framework import viewsets
from .serializers import ProductSerializer,ProductDetailSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

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
    queryset = Products.objects.all()
    
    def retrieve(self, request, pk):
        showed_product = get_object_or_404(self.queryset, pk=pk)
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

    def get_queryset(self):
        products = Products.objects.select_related('brand').prefetch_related('category').filter(is_delete=False)
        category = self.kwargs.get('cat')
        if category:
            products = products.filter(category__slug=category)
        brand = self.kwargs.get('brand')
        if brand:
            products = products.filter(brand__slug=brand)
        return products


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def like_product(request, pk):
    product = get_object_or_404(Products, pk=pk)
    user = request.user
    liked = False

    if user in product.likes.all():
        product.likes.remove(user)
    else:
        product.likes.add(user)
        liked = True
    product.likes_count = product.likes.count()
    product.save()
    return Response({'liked': liked, 'status': 'ok'})