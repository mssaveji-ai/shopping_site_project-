from django.urls import path
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("products-list", views.ProductsViewSet, basename="product")

urlpatterns = [
    path('product-detail/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
    path('api/products-list/category/<slug:cat>/', views.ProductsViewSet.as_view({'get':'list'}), name='products-category-list'),
    path('api/products-list/brand/<slug:brand>/', views.ProductsViewSet.as_view({'get':'list'}), name='products-brand-list'),
    path('api/product-detail-api/<int:pk>/', views.ProductDetailViewSet.as_view({'get':'retrieve'}), name='product-detail-api'),
    path('api/review/create/', views.ReviewAPI.as_view(), name='review-create-api'),
    path('api/review/product/<int:product_id>/', views.ProductReviewListAPI.as_view(), name='review-product-list-api'),
    path('api/review/update/<int:review_id>/', views.UpdateReviewAPI.as_view(), name='review-update-api'),
    path('api/review/delete/<int:review_id>/', views.DeleteReview.as_view(), name='review-delete-api'),
    path('api/wishlist/add/', views.AddWishList.as_view(), name='wishlist-add-api'),
    path('api/wishlist/remove/<int:product_id>/', views.RemoveWishList.as_view(), name='wishlist-remove-api'),
    path('api/wishlist/', views.WishlistAPI.as_view(), name='wishlist-api'),
    path('api/like/<int:pk>/', views.like_product , name='like-toggle'),
    path("api/", include(router.urls)),
]
