import logging
from rest_framework.decorators import action
from csv import DictWriter

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, redirect, reverse, get_object_or_404, resolve_url
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from timeit import default_timer

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django_filters.rest_framework import DjangoFilterBackend

from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView,
    ListView,
    DeleteView,
    DetailView,
    CreateView,
    UpdateView
)

from .models import Product, Order, ProductImage

from .common import save_csv_products
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.request import Request
from rest_framework.response import Response
from .serializers import ProductSerializer, OrderSerializer
from rest_framework.views import APIView

from .forms import ProductForm, OrderForm, GroupForm

from django.contrib.syndication.views import Feed

from django.views import View

from drf_spectacular.utils import extend_schema


log = logging.getLogger(__name__)


@extend_schema('description = Product views CRUD')
class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['name', 'description']
    filterset_fields = [
        'name',
        'description',
        'price',
        'discount',
        'archived',
    ]
    ordering_fields = [
        'name',
        'price',
        'discount',
    ]

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    @action(methods=['get'], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type='text/csv')
        filename = 'products-export.csv'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            'name',
            'description',
            'price',
            'discount',
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(
        detail=False,
        methods=['post'],
        parser_classes=[MultiPartParser]
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
                request.FILES['file'],
                encoding=request.encoding,
             )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['user', 'delivery_address']
    filterset_fields = [
        'delivery_address',
        'user',
        'products',
        'promocode',
    ]
    ordering_fields = [
        'pk',
        'delivery_address',
        'user',
        'products',
    ]


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 999),
        ]

        context = {
            'time_running': default_timer(),
            'products': products,
            'items': 5,
        }
        log.debug('Products for shop index: %s', products)
        log.info('Rendering shop index')
        print('shop imdex context', context)
        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            'form': GroupForm(),
            'groups': Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductDetailView(DetailView):
    template_name = 'shopapp/products-dateils.html'
    queryset = Product.objects.prefetch_related('images')
    context_object_name = 'product'

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        product = get_object_or_404(Product, pk=pk)
        context = {
            'product': product
        }
        return render(request, 'shopapp/products-dateils.html', context=context)


class ProductListView(ListView):
    template_name = 'shopapp/products-list.html'
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False)


class CreateProductView(CreateView):
    # permission_required = 'shopapp.add_product'
    queryset = Product.objects.select_related('user')
    fields = 'name', 'price', 'description', 'discount', 'preview'
    template_name = 'shopapp/product_form.html'
    success_url = reverse_lazy('shopapp:products_list')

    # def form_valid(self, form):
    #     form.instance.created_by = self.request.user
    #     return super().form_valid(form)


class UpdateProductView(PermissionRequiredMixin, UpdateView):
    permission_required = 'shopapp.change_product'
    # template_name = 'shopapp/product_form.html'
    fields = 'name', 'price', 'description', 'discount', 'preview'
    template_name_suffix = '_update_form'
    model = Product
    # form_class = ProductForm

    def get_success_url(self):
        return reverse(
            'shopapp:product_details',
            kwargs={'pk': self.object.pk}
        )

    # def form_valid(self, form):
    #     response = super().form_valid(form)
    #     for image in form.files.getlist('images'):
    #         ProductImage.objects.create(
    #             product=self.object,
    #             image=image,
    #         )
    #     return response
    #
    # def get_queryset(self):
    #     return Product.objects.filter(created_by=self.request.user).select_related('created_by')


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class LatestProductsFeed(Feed):
    title = 'Products (latest)'
    description = 'Products description'
    link = reverse_lazy('shopapp:products_list')

    def items(self):
        return (
            Product.objects.only(
                'name', 'description',
                'price', 'preview'
            )[:5]
        )

    def item_title(self, item: Product):
        return item.name

    def item_link(self, item: Product):
        return item.description


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )
    context_object_name = 'orders'


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = 'shopapp.view_order'
    queryset = (
        Order.objects
        .select_related('user')
        .prefetch_related('products')
    )


def create_order(request: HttpRequest):
    if request.method == 'GET':
        form = OrderForm(request.GET)
        if form.is_valid():
            form.save()
            url = reverse('shopapp:orders_list')
            return redirect(url)
    else:
        form = OrderForm()

    context = {
        'form': form
    }
    return render(request, 'shopapp/create-order.html', context=context)


class OrderCreateView(CreateView):
    queryset = Order.objects.select_related('user').prefetch_related('products')
    success_url = 'shopapp:orders_list'
    fields = 'user', 'products', 'delivery_address', 'promocode'
    template_name = 'shopapp/order_form.html'


class OrderUpdateView(UpdateView):
    queryset = Order.objects.select_related('user').prefetch_related('products')
    fields = 'user', 'products', 'delivery_address', 'promocode'
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse(
            'shopapp:order_details',
            kwargs={'pk': self.object.pk}
        )


class UsersOrderList(LoginRequiredMixin, ListView):
    queryset = Order
    context_object_name = 'orders'
    template_name = 'shopapp/users-orders-list.html'

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise Http404('User not found')
        return Order.objects.filter(user_id=user_id)


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy('shopapp:orders_list')


class OrderExportView(UserPassesTestMixin, View):
    queryset = Order.objects.select_related('user').prefetch_related('products').all()
    template_name = 'shopapp:order-export.html'

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request: HttpRequest) -> JsonResponse:

        orders = Order.objects.select_related('user').prefetch_related('products').all()
        orders_data = [
            {'order_id': order.pk,
             'address': order.delivery_address,
             'promocode': order.promocode,
             'user_id': order.user.pk,
             'products_id_list': [x.pk for x in order.products.all()],
            }
            for order in orders
        ]

        return JsonResponse({'orders': orders_data})


class UserOrderExportView(View):
    model = Order
    template_name = 'shopapp/user_order_export.html'

    def get(self, request: HttpRequest, user_id) -> JsonResponse:
        cache_key = 'orders_data_export'
        orders_data = cache.get(cache_key)
        if orders_data is None:
            orders = Order.objects.filter(user_id=user_id).all()
            orders_data = [
                {'order_id': order.pk,
                 'address': order.delivery_address,
                 'promocode': order.promocode,
                 'user_id': order.user.pk,
                 'products_id_list': [x.pk for x in order.products.all()],
                }
                for order in orders
            ]
            cache.set(cache_key, orders_data, 300)

        return JsonResponse({'orders': orders_data})


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = 'products_data_export'
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by('pk').all()
            products_data = [
                {
                    'pk': product.pk,
                    'name': product.name,
                    'price': product.price,
                    'archived': product.archived,
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)
        return JsonResponse({'products': products_data})
