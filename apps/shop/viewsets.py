import copy
import json
from django.conf import settings
from django.db.models import Q
from django.db import transaction
from apps.shop.payment_method import PAYMENT_METHODS, PAYMENT_METHOD_KEYS
from utils.hashids import Hashids
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import list_route, api_view, authentication_classes, permission_classes, detail_route
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from apps.common.viewsets import BaseViewSet
from apps.shop.serializers import (
    CreateProductSerializer,
    ManagerProductSerializer,
    CategorySerializer,
    SliderSerializer,
    SampleFormsSerializer,
    ProductBoxSerializer,
    SingleProductSerializer,
    InvoiceSerializer,
    BasketSerializer,
    FilesSerializer,
    UpdateProductSerializer)
from apps.shop.models import (
    Product, Category,
    SampleForms,
    ProductImage, ProductFile,
    ProductSampleFormFields,
    ShopSlider, Basket, Invoice,
    InvoiceProduct
)
from utils.user_type import get_user_type


class ProductManagerViewSet(BaseViewSet):
    queryset = Product.objects.all()
    serializer_class = ManagerProductSerializer

    @list_route(url_path='categories', methods=['get'])
    def product_categories(self, request):
        queryset = Category.objects.filter(parent=None)

        serializer = CategorySerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @detail_route(url_path='sub_categories', methods=['get'])
    def product_sub_categories(self, request, pk=None):
        queryset = Category.objects.filter(parent_id=pk)

        serializer = CategorySerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @list_route(url_path='delete', methods=['post'])
    def delete(self, request):
        product = Product.objects.filter(id=request.data.get('product_id'))
        if product.exists():
            product.update(editor_id=request.user.id, deleted=True)
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK)

    @list_route(url_path='sample_forms', methods=['get'])
    def get_sample_forms(self, request):
        queryset = SampleForms.objects.all()

        serializer = SampleFormsSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @list_route(url_path='sample_form', methods=['get'])
    def get_sample_form(self, request):
        sample_id = request.query_params.get('id')
        queryset = SampleForms.objects.filter(id=sample_id).prefetch_related('groups__sampleformfields_set')
        response = {}
        if queryset.exists():
            sample_form = queryset.get()
            response["title"] = sample_form.title
            response["groups"] = []
            for group in sample_form.groups.all():
                dict_group = {
                    "label": group.title,
                    "id": group.id,
                    "fields": []
                }
                for field in group.sampleformfields_set.all():
                    dict_group["fields"].append({
                        "label": field.title,
                        "required": field.is_required,
                        "presentation": field.presentation,
                        "id": field.id,
                        "type": field.type,
                    })
                response["groups"].append(dict_group)

            return Response(response, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        data = copy.copy(request.data)
        data["creator"] = request.user.id
        data["editor"] = request.user.id
        self.serializer_class = CreateProductSerializer
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(deleted=False).order_by("-created_at")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        with transaction.atomic():
            product = serializer.save()
            data = self.request.data
            self.save_image(data.getlist('images[]', []), product)
            self.save_file(data.getlist('files[]', []), product)
            self.save_sample_form(json.loads(data.get('sample_forms[]', '[]')), product)

    @staticmethod
    def save_image(images, product):
        for img in images:
            image_model = ProductImage()
            image_model.image = img
            image_model.product = product
            image_model.save()

    @staticmethod
    def save_file(files, product):
        for file in files:
            file_model = ProductFile()
            file_model.file = file
            file_model.product = product
            file_model.save()

    @staticmethod
    def save_sample_form(sample_forms, product):
        ProductSampleFormFields.objects.filter(product_id=product.id).delete()
        if not product.sample_form:
            return

        groups = SampleForms.objects.get(id=product.sample_form.id).groups.all()

        list_fields = []
        for group in groups:
            for field in group.sampleformfields_set.all():
                list_fields.append(field.id)

        # if len(list_fields) != len(sample_forms):
        #     raise ValidationError({"sample_form": ""}, code=status.HTTP_400_BAD_REQUEST)

        for r_field in sample_forms:
            if r_field['id'] not in list_fields:
                continue

            product_sample_form = ProductSampleFormFields()
            product_sample_form.product = product
            product_sample_form.sample_form_field_id = r_field['id']
            product_sample_form.value = r_field['value']
            product_sample_form.save()

    @list_route(url_path='update', methods=['post'])
    def product_update(self, request):
        data = copy.copy(request.data)
        # data["editor_id"] = request.user.id
        product_id = data.get('product_id')

        instance = self.queryset.filter(id=product_id)
        if instance.exists():
            self.serializer_class = UpdateProductSerializer
            serializer = self.get_serializer(instance.get(), data=request.data, partial=data)
            serializer.is_valid(raise_exception=True)
            # Todo how to update editor
            self.perform_update(serializer)
            instance.update(editor_id=request.user.id)

            return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    def perform_update(self, serializer):
        product = serializer.save()
        with transaction.atomic():
            data = self.request.data
            self.update_images(data, product)
            self.update_files(data, product)
            self.save_sample_form(json.loads(data.get('sample_forms[]', '[]')), product)

    def update_images(self, data, product):
        images = data.getlist('images[]', [])
        try:
            delete_images = json.loads(data.get('deleted_images', '[]'))
        except Exception as e:
            raise ValidationError(e, code=status.HTTP_400_BAD_REQUEST)

        self.save_image(images, product)
        if delete_images:
            _d_images = ProductImage.objects.filter(
                id__in=delete_images,
                product_id=product.id,
                archive=False
            )
            if _d_images:
                _d_images.update(archive=True)

    def update_files(self, data, product):
        files = data.getlist('files[]', [])
        self.save_file(files, product)

        try:
            delete_files = json.loads(data.get('deleted_files', '[]'))
        except Exception as e:
            raise ValidationError(e, code=status.HTTP_400_BAD_REQUEST)

        if delete_files:
            _d_files = ProductFile.objects.filter(
                id__in=delete_files,
                product_id=product.id,
                archive=False
            )
            if _d_files:
                _d_files.update(archive=True)


class ProductViewSet(BaseViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductBoxSerializer

    def list(self, request, *args, **kwargs):
        pass

    @list_route(url_path='special_category', methods=['get'])
    def special_category(self, request):
        """
        :param request:
        :return: special categories from product
        """

        res = []

        self.newest_product(res)
        # self.newest_product(res)
        # self.newest_product(res)
        # self.newest_product(res)

        return Response(res)

    @list_route(url_path='search', methods=['get'])
    def search(self, request):
        """
          list product
        :param request:
        :return: return all product filter by gender and published and param get
        """
        params = self.get_params(request)
        query, orders = self.get_query(params)
        queryset = self.queryset.filter(query).order_by(*orders)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def newest_product(self, res):

        user_type = get_user_type(self.request.user)
        if user_type == 'student':
            products = self.queryset.filter(
                gender__in=[self.request.user.baseuser.gender, 'both'],
                published=True,
                deleted=False,
                for_student=True,
            ).order_by('-created_at')[:12]
        elif user_type == 'teacher':
            products = self.queryset.filter(
                gender__in=[self.request.user.baseuser.gender, 'both'],
                published=True,
                deleted=False,
                for_teacher=True
            ).order_by('-created_at')[:12]

        # products = self.queryset.filter(
        #     gender__in=[self.request.user.baseuser.gender, 'both'],
        #     published=True
        # ).order_by()[:12]

        _dict = {
            "query_param": 'order=newest',
            "title": "تازه ترین ها",
            "products": self.get_serializer(products, many=True).data
        }
        res.append(_dict)

    @staticmethod
    def get_params(request):
        query_params = request.query_params.copy()
        dict_params = {}
        list_param_int = [
            'price_start', 'price_end', 'has_discount'
        ]
        list_param_str = ['text', 'order']
        for key, value in query_params.items():
            if key in list_param_int:
                if query_params[key].isdigit():
                    dict_params[key] = int(value)
                    continue
            if key in list_param_str:
                dict_params[key] = str(value)
        return dict_params

    def get_query(self, dict_params):
        orders = []
        q_object = Q()

        q_object.add(Q(gender__in=[self.request.user.baseuser.gender, 'both']), Q.AND)
        q_object.add(Q(published=True), Q.AND)
        q_object.add(Q(deleted=False), Q.AND)

        if 'order' in dict_params:
            if dict_params["order"] == "newest":
                orders.append('-created_at')

            if dict_params["order"] == "price_high":
                orders.append('-price')

            if dict_params["order"] == "price_low":
                orders.append('price')

        if 'category' in dict_params:
            q_object.add(Q(category_id=dict_params['category']), Q.AND)

        if 'has_discount' in dict_params and dict_params['has_discount'] == 1:
            q_object.add(Q(has_discount=dict_params['has_discount']), Q.AND)

        if 'text' in dict_params:
            q_object.add(Q(title__regex=dict_params['text']), Q.AND)

        if 'price_start' in dict_params:
            q_object.add(Q(price__gte=dict_params['price_start']), Q.AND)

        if 'price_end' in dict_params:
            q_object.add(Q(price__lte=dict_params['price_end']), Q.AND)

        # برای فیلتر کردن محصولات دانش آموزان و مربی ها
        user_type = get_user_type(self.request.user)
        if user_type == 'student':
            q_object.add(Q(for_student=True), Q.AND)
        elif user_type == 'teacher':
            q_object.add(Q(for_teacher=True), Q.AND)

        return q_object, orders

    @list_route(url_path='slider', methods=['get'])
    def slider(self, request):
        """
        :param request:
        :return: slider from product
        """
        # queryset = ShopSlider.objects.all()
        user_type = get_user_type(request.user)
        if user_type == 'student':
            queryset = ShopSlider.objects.filter(for_student=True)
        elif user_type == 'teacher':
            queryset = ShopSlider.objects.filter(for_teacher=True)
        else:
            queryset = []
        queryset = queryset.filter(Q(gender=request.user.baseuser.gender) | Q(gender="both"))
        serializer = SliderSerializer(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        :param request:
        :return: return product by gender
        """
        self.serializer_class = SingleProductSerializer
        instance = self.get_object()

        serializer = self.get_serializer(instance)
        product = serializer.data
        product["groups"] = self.create_sample_form_field(product)
        user_type = get_user_type(self.request.user)

        if instance.deleted:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if user_type == 'student':
            if not instance.for_student:
                return Response(status=status.HTTP_403_FORBIDDEN)
        elif user_type == 'teacher':
            if not instance.for_teacher:
                return Response(status=status.HTTP_403_FORBIDDEN)

        return Response(product)

    @staticmethod
    def create_sample_form_field(product):
        """
        :param product:
        :return: return groups from sample_form_field

        Groups sample form field from product

        """
        try:
            sample_form = SampleForms.objects.get(id=product["sample_form"])
        except:
            product["groups"] = []
            return

        groups = []
        for group in sample_form.groups.all():
            _group = {
                'id': group.id,
                'title': group.title
            }
            sample_forms = []
            for pro_item in product["sample_form_fields"]:
                for sample_form_field in group.sampleformfields_set.all():
                    if pro_item["sample_form_field"] == sample_form_field.id:
                        _dict = {
                            "title": sample_form_field.title,
                            "value": pro_item["value"],
                            "order": sample_form_field.order if sample_form_field.order else 0
                        }
                        sample_forms.append(_dict)

            if sample_forms:
                _group["sample_form_fields"] = sorted(sample_forms, key=lambda x: x["order"], reverse=False)
                groups.append(_group)

        return groups


class BasketViewSet(BaseViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer

    def list(self, request, *args, **kwargs):
        """
          list product
        :param request:
        :return: return all product from user in basket
        """
        result = self.get_basket_from_user(request)

        return Response(result)

    def get_basket_from_user(self, request):
        products = [item["product_id"] for item in list(self.queryset.filter(user=request.user).values('product_id'))]
        queryset = Product.objects.filter(
            gender__in=[request.user.baseuser.gender, 'both'],
            published=True,
            id__in=products
        )
        total_price = 0
        total_discount = 0
        for product in queryset:
            if product.is_free:
                continue

            if product.has_discount:
                total_discount += int(product.price * (product.discount / 100))

            total_price += product.price
        serializer = ProductBoxSerializer(queryset, many=True)
        result = {
            "products": serializer.data,
            'total_price': total_price,
            'total_discount': total_discount,
            'payable': total_price - total_discount,
        }
        return result

    def create(self, request, *args, **kwargs):
        data = copy.copy(request.data)
        data["user"] = request.user.id

        self.queryset.filter(user_id=data["user"], product_id=data["product"]).delete()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

    @list_route(url_path='get_count_product_in_basket', methods=['get'])
    def get_count_product_in_basket(self, request):
        """
        :param request:
        :return: count of product in basket
        """

        count = self.queryset.filter(user_id=request.user.id).count()

        return Response({"count": count})

    @list_route(url_path='delete', methods=['post'])
    def delete(self, request):
        """
        :param request:
        :return: remove product from basket
        """
        self.queryset.filter(user_id=request.user.id, product_id=request.data.get("product")).delete()
        result = self.get_basket_from_user(request)

        return Response(result)


class InvoiceViewSet(BaseViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = copy.copy(request.data)
        data["user"] = request.user.id
        payment_method = data.get('payment_method')
        if payment_method not in PAYMENT_METHOD_KEYS:
            raise ValidationError({"message": "payment_method is not valid"}, code=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        url = self.generate_payment_url(payment_method)

        return Response(
            {
                'url': url,
                'order_code': serializer.data["code"],
            },
            status=status.HTTP_200_OK
        )

    def perform_create(self, serializer):
        invoice = serializer.save()
        hash_ids = Hashids(min_length=8, salt=settings.SECRET_KEY)
        hash_id = hash_ids.encode(invoice.id)
        invoice.code = hash_id
        invoice.save()
        products = Basket.objects.filter(user_id=self.request.user.id)
        if not products:
            raise ValidationError({"message": "basket is empty"}, code=status.HTTP_400_BAD_REQUEST)

        for product in products:
            _model = InvoiceProduct()
            _model.product = product.product
            _model.invoice = invoice
            _model.save()

        products.delete()

    @staticmethod
    def generate_payment_url(payment_method):
        return "https://ebanking.bankmellat.ir/ebanking/sessionExpired.bm"

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(user_id=request.user.id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.queryset.get(code=kwargs.get("pk"))
        queryset = instance.invoiceproduct_set.all()
        total_price = 0
        total_discount = 0
        files = []
        for product in queryset:
            for file in product.product.productfile_set.all():
                files.append(FilesSerializer(file, many=False).data)

            if product.is_free:
                continue

            if product.has_discount:
                total_discount += int(product.price * (product.discount / 100))

            total_price += product.price

        result = {
            "code": instance.code,
            "files": files,
            'total_price': total_price,
            'total_discount': total_discount,
            'payable': total_price - total_discount,
        }

        return Response(result)


@api_view(['GET'])
@authentication_classes((JSONWebTokenAuthentication, SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def list_payment_method(request):
    return Response(PAYMENT_METHODS)
