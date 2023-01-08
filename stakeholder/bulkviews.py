from rest_framework import generics
from rest_framework.parsers import JSONParser
from stakeholder.models import Stakeholder
from stakeholder.serializers import StakeholderSerializer
from utilities.bulkviewmixins import BulkDeleteMixin, BulkPatchMixin


class BulkStakeholderViews(BulkDeleteMixin, generics.GenericAPIView):
    serializer_class = StakeholderSerializer
    queryset = Stakeholder.objects.all()
