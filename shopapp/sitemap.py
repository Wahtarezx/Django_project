from django.contrib.sitemaps import Sitemap

from .models import Product


class ShopSitemap(Sitemap):
    changefreq = 'newer'
    priority = 0.8

    def items(self):
        return Product.objects.filter(archived=False).order_by('-created_at')

    def lastmod(self, obj: Product):
        return obj.created_at
