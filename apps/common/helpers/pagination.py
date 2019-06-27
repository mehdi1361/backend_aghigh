from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):

        try:
            next_page = self.page.next_page_number()
        except:
            next_page = None

        try:
            previous_page = self.page.previous_page_number()
        except:
            previous_page = None

        return Response({
           'next': next_page,
           'previous': previous_page,
           'count': self.page.paginator.count,
           'results': data
        })
