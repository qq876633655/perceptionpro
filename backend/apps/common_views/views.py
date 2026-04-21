from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated


class BaseModelViewSet(ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
