from django.views.generic.base import TemplateView
from products.models import Products, ProductCategory
from django.db.models import Count, Prefetch,Sum
from utiles.convertors import group_list
from rest_framework.views import APIView
from rest_framework.response import Response
from products.serializers import ProductSerializer, ProductCategorySerializer
from rest_framework.permissions import AllowAny

class home_page(TemplateView):
    template_name = 'home/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_products = Products.objects.filter(in_stock=True,is_delete=False).order_by('-id')[:12]
        context ['latest_products'] = group_list (latest_products)
        categories = ProductCategory.objects.filter(is_delete=False)[:8]
        context ['categories'] = categories
        most_baught_products = Products.objects.filter(product_basket__order__is_paid=True).annotate(baught_count=Sum('product_basket__count')).order_by('-baught_count')[:12]
        context['most_baught_products'] = most_baught_products
        most_visited_products = Products.objects.filter(in_stock=True, is_delete=False).annotate(visited_count=Sum('productvisit')).order_by('-visited_count')[:6]
        context['most_visited_products'] = group_list(most_visited_products)
        return context

class Home_APIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        latest_products = Products.objects.filter(in_stock=True,is_delete=False).order_by('-id')[:12]
        categories = ProductCategory.objects.filter(is_delete=False)[:8]
        most_baught_products = Products.objects.filter(product_basket__order__is_paid=True).annotate(baught_count=Sum('product_basket__count')).order_by('-baught_count')[:12]
        most_visited_products = Products.objects.filter(in_stock=True, is_delete=False).annotate(visited_count=Sum('productvisit')).order_by('-visited_count')[:6]
        
        return Response({
            "latest_products": ProductSerializer(latest_products, many=True).data,
            "categories": ProductCategorySerializer(categories, many=True).data,
            "most_baught_products": ProductSerializer(most_baught_products, many=True).data,
            "most_visited_products": ProductSerializer(most_visited_products, many=True).data,
        })