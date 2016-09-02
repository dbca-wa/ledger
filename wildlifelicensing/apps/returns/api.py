from rest_framework import routers
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from wildlifelicensing.apps.returns.models import ReturnType, ReturnTable, ReturnRow


class ReturnTableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReturnTable.objects.all()
    renderer_classes = (JSONRenderer,)
    authentication_classes = []


router = routers.DefaultRouter()
router.register(r'^', ReturnTableViewSet)
print('router', router.urls)
