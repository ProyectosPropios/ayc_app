from django.shortcuts import render
from rest_framework import viewsets

from users.permissions import IsAdminRole

from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminRole,)
    serializer_class = CustomerSerializer
    queryset = Customer.objects.select_related("created_by").all()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
