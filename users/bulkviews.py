from django.contrib.auth.models import Group
from rest_framework import generics
from users.models import User

from users.serializers import ConciseUserSerializer, GroupSerializer
from utilities.bulkviewmixins import BulkDeleteMixin


class BulkGroupView(BulkDeleteMixin, generics.GenericAPIView):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()


class BulkAccountView(BulkDeleteMixin, generics.GenericAPIView):
    serializer_class = ConciseUserSerializer
    queryset = User.objects.all()
