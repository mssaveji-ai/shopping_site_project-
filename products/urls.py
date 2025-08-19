from django.urls import path
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("products-list/", views.ProductsViewSet, basename="product")

urlpatterns = [
    path('products-list/category/<slug:cat>/', views.ProductsViewSet.as_view({'get':'list'}), name='products-category-list'),
    path('products-list/brand/<slug:brand>/', views.ProductsViewSet.as_view({'get':'list'}), name='products-brand-list'),
    path('product-detail/<int:pk>/', views.ProductDetailViewSet.as_view({'get':'retrieve'}), name='product-detail'),
    path('like/<int:pk>/', views.like_product , name='like-toggle'),
    path("api/", include(router.urls)),
]