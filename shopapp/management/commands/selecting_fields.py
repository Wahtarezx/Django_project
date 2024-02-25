from django.contrib.auth.models import User
from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Start demo select fields')
        user_info = User.objects.values_list('username', flat=True)
        print(list(user_info))
        for u_inf in user_info:
            print(u_inf)


        # product_values = Product.objects.values('pk', 'name',)
        #
        # for p_value in product_values:
        #     print(p_value)

        self.stdout.write('Done')

