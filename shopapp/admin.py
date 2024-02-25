from django.urls import path

from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from .common import save_csv_products, save_csv_orders
from .models import Product, Order, ProductImage
from .admin_mixins import ExportAsCSVMixin
from .forms import CSVImportForm


class OrderInline(admin.TabularInline):
    model = Product.orders.through


class ImageInline(admin.StackedInline):
    model = ProductImage


@admin.action(description='Unarchived product')
def mark_unarchiced(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.action(description='Archive product')
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet) -> None:
    queryset.update(archived=True)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = 'shopapp/products_changelist.html'
    actions = [
        mark_archived,
        mark_unarchiced,
    ]

    inlines = [
        OrderInline,
        ImageInline,
    ]

    list_display = 'pk', 'name', 'description_short', 'price', 'discount', 'archived',
    list_display_links = 'pk', 'name',
    search_fields = 'pk', 'name', 'description'

    fieldsets = [
        (None, {
            'fields': ('name', 'description',),
        }),
        ('Price Information',{
            'fields': ('price', 'discount',),
        }),
        ('Images', {
            'fields': ('preview',),
        }),
        ('Extra Oprions', {
            'fields': ('archived',),
            'classes': ('collapse',),
            'description': ' Extra Option. Field "archived"'
        })
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + '...'

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == 'GET':
            form = CSVImportForm()
            context = {
                'form': form
            }
            return render(request, 'admin/csv_form.html', context=context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                'form': form
            }
            return render(request, 'admin/csv_form.html', context=context, status=400)

        save_csv_products(
            file=form.files['csv_file'].file,
            encoding=request.encoding
        )
        self.message_user(request, 'Data from CSV imported')
        return redirect('..')


    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                'import-products-csv/',
                self.import_csv,
                name='import_products_csv',
            ),
        ]
        return new_urls + urls

class ProductInline(admin.TabularInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = 'shopapp/orders_changelist.html'

    inlines = [
        ProductInline
    ]
    list_display = 'pk', 'delivery_address', 'promocode', 'created_at', 'user_verbose'

    def get_queryset(self, request):
        return Order.objects.select_related('user').prefetch_related('products')

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == 'GET':
            form = CSVImportForm()
            context = {
                'form': form
            }
            return render(request, 'admin/csv_form.html', context=context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                'form': form
            }
            return render(request, 'admin/csv_form.html', context=context, status=400)

        save_csv_orders(
            file=form.files['csv_file'].file,
            encoding=request.encoding,
        )
        self.message_user(request, 'Data from CSV imported')
        return redirect('..')

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-orders-csv/",
                self.import_csv,
                name='import_orders_csv',
            ),
        ]
        return new_urls + urls
