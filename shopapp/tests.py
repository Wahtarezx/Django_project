from string import ascii_letters

from django.contrib.auth.models import User, Permission
from django.urls import reverse

from random import choices


from django.test import TestCase

from django_skillbox import settings
from .models import Product, Order
from .utils import add_two_numbers


class AddTwuNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class CreateProductViewTestCase(TestCase):
    def setUp(self):
        self.product_name = ''.join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product_view(self):
        response = self.client.post(
            reverse('shopapp:create_product'),
            {
                'name': self.product_name,
                'price': '123.45',
                'description': 'A good product description',
                'discount': '10',
            }
        )

        self.assertRedirects(response, reverse('shopapp:products_list'))
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.product = Product.objects.create(name='Mega Bob')

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def test_product_details_view(self):
        response = self.client.get(reverse(
            'shopapp:product_details', kwargs={'pk': self.product.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product.name)


class ProductListViewTestCase(TestCase):
    fixtures = [
        'product-fixture.json'
    ]

    def test_product_list_view(self):
        response = self.client.get(reverse('shopapp:products_list'))
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context['products']),
            transform=lambda p: p.pk
        )
        self.assertTemplateUsed(response, 'shopapp/products-list.html')


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='BigBob', password='qwerty')
        cls.user = User.objects.create_user(**cls.credentials)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.login(**self.credentials)

    def test_orders_list_view(self):
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertContains(response, 'Orders')

    def test_order_list_non_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='BigBob', password='qwerty')
        cls.user = User.objects.create_user(**cls.credentials)
        cls.user.user_permissions.add(Permission.objects.get(codename='view_order'))
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.login(**self.credentials)
        self.order = Order.objects.create(
            promocode='promobaza228',
            delivery_address='LevBul56',
            user_id=self.user.id
        )

    def tearDown(self):
        self.order.delete()

    def test_order_detail_view(self):
        response = self.client.get(reverse('shopapp:order_details', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.delivery_address)


class OrderExportViewTestCase(TestCase):
    fixtures = [
        'order-fixture.json'
    ]

    @classmethod
    def setUpClass(cls):
        cls.credentials = dict(username='BigBob', password='qwerty')
        cls.user = User.objects.create_user(**cls.credentials)
        cls.user.is_staff = True
        cls.user.save()


    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.login(**self.credentials)

    def test_order_export_view(self):
        response = self.client.get(reverse(
            'shopapp:order_export'),
        )
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.all()
        expected_data = [
            {
                'order_id': order.pk,
                'address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user.pk,
                'products_id_list': [x.pk for x in order.products.all()],
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(
            orders_data['orders'],
            expected_data
        )



