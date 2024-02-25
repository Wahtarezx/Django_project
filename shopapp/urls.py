from django.urls import path, include

from rest_framework.routers import DefaultRouter

from django.views.decorators.cache import cache_page

from .views import (ShopIndexView,
                    GroupsListView,
                    ProductDetailView,
                    ProductListView,
                    OrdersListView,
                    OrderDetailView,
                    UpdateProductView,
                    ProductDeleteView,
                    OrderUpdateView,
                    CreateProductView,
                    OrderCreateView,
                    OrderDeleteView,
                    OrderExportView,
                    ProductViewSet,
                    OrderViewSet,
                    ProductsDataExportView,
                    LatestProductsFeed,
                    UsersOrderList,
                    UserOrderExportView,
                    )


orders_router = DefaultRouter()
orders_router.register('orders', OrderViewSet)

product_router = DefaultRouter()
product_router.register('products', ProductViewSet)

app_name = 'shopapp'

urlpatterns = [
    path('', ShopIndexView.as_view(), name='index'),
    path('api/', include(product_router.urls)),
    path('api/', include(orders_router.urls)),
    path('groups/', GroupsListView.as_view(), name='groups_list'),
    path('products/', ProductListView.as_view(), name='products_list'),
    path('products/latest/feed/', LatestProductsFeed(), name='products_feed'),
    path('products/export/', ProductsDataExportView.as_view(), name='products-export'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_details'),
    path('products/<int:pk>/update/', UpdateProductView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('products/create/', CreateProductView.as_view(), name='create_product'),
    path('orders/', OrdersListView.as_view(), name='orders_list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_details'),
    path('orders/<int:pk>/update/', OrderUpdateView.as_view(), name='order_update'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),
    path('orders/create/', OrderCreateView.as_view(), name='create_order'),
    path('orders/export/', OrderExportView.as_view(), name='order_export'),
    path('users/<int:user_id>/orders/', UsersOrderList.as_view(), name='users_orders_list'),
    path('orders/<int:user_id>/export/', UserOrderExportView.as_view(), name='users_orders_export'),
]
