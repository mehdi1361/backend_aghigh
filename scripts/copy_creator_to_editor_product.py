# -*- coding: utf-8 -*-
from apps.shop.models import Product


def get_all_and_replace():
    products = Product.objects.all()
    for product in products:
        product.editor = product.creator
        product.save()
