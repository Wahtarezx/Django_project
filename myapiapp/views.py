from django.contrib.auth.models import Group
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.mixins import ListModelMixin

from .serializers import GroupSerializer


@api_view()
def hello_world_view(request: Request) -> Response:
    return Response({'message': 'Hello world!'})


# class GroupListView(ListModelMixin, GenericAPIView):
#     queryset = Group.objects.all()
#     serializer_class = GroupSerializer
#
#     def get(self, request: Request) -> Response:
#         return self.list(request)


class GroupListView(ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
