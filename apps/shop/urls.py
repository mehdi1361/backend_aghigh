from dashboard.router import api_v1_router
from apps.shop.viewsets import ProductManagerViewSet, ProductViewSet, BasketViewSet, InvoiceViewSet
from apps.shop.viewsets import list_payment_method
from django.conf.urls import url


api_v1_router.register(prefix=r'product_manager', viewset=ProductManagerViewSet, base_name='product_manager')
api_v1_router.register(prefix=r'product', viewset=ProductViewSet, base_name='product')
api_v1_router.register(prefix=r'basket', viewset=BasketViewSet, base_name='basket')
api_v1_router.register(prefix=r'invoice', viewset=InvoiceViewSet, base_name='invoice')

urlpatterns = [
    url(r'^payment_methods/$', list_payment_method, name="payment_methods"),
]
