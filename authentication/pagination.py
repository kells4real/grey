from rest_framework import pagination
from rest_framework.response import Response
from collections import OrderedDict
import math


class StandardStudentPagination(pagination.PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'per_page'
    max_page_size = 1000

    def get_paginated_response(self, data):
        student_count = self.page.paginator.count
        last_page = math.ceil(self.page.paginator.count / self.page_size)
        return Response(OrderedDict([
             ('last_page', last_page),
             ('countItemsOnPage', self.page_size),
             ('current_page', self.page.number),
             ('next_page', self.get_next_link()),
             ('previous_page', self.get_previous_link()),
             ('total_students', student_count),
             ('results', data)
         ]))


class StandardAllStudentPagination(pagination.PageNumberPagination):
    page_size = 10
    page_query_param = 'page'
    page_size_query_param = 'per_page'
    max_page_size = 1000

    def get_paginated_response(self, data):
        student_count = self.page.paginator.count
        last_page = math.ceil(self.page.paginator.count / self.page_size)
        return Response(OrderedDict([
             ('last_page', last_page),
             ('countItemsOnPage', self.page_size),
             ('current_page', self.page.number),
             ('next_page', self.get_next_link()),
             ('previous_page', self.get_previous_link()),
             ('total_students', student_count),
             ('results', data)
         ]))


class StandardUsersPagination(pagination.PageNumberPagination):
    page_size = 4
    page_query_param = 'page'
    page_size_query_param = 'per_page'
    max_page_size = 1000

    def get_paginated_response(self, data):
        student_count = self.page.paginator.count
        last_page = math.ceil(self.page.paginator.count / self.page_size)
        return Response(OrderedDict([
             ('last_page', last_page),
             ('countItemsOnPage', self.page_size),
             ('current_page', self.page.number),
             ('next_page', self.get_next_link()),
             ('previous_page', self.get_previous_link()),
             ('total_students', student_count),
             ('results', data)
         ]))
