from __future__ import absolute_import, unicode_literals

from django.apps import apps
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from mayan.apps.dashboards.classes import DashboardWidgetNumeric
from mayan.apps.documents.permissions import permission_document_view

from .icons import icon_dashboard_checkouts
from .permissions import permission_document_checkout_detail_view


class DashboardWidgetTotalCheckouts(DashboardWidgetNumeric):
    icon_class = icon_dashboard_checkouts
    label = _('Checkedout documents')
    link = reverse_lazy(viewname='checkouts:document_checkout_list')

    def render(self, request):
        AccessControlList = apps.get_model(
            app_label='acls', model_name='AccessControlList'
        )
        DocumentCheckout = apps.get_model(
            app_label='checkouts', model_name='DocumentCheckout'
        )
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_checkout_detail_view,
            queryset=DocumentCheckout.objects.checked_out_documents(),
            user=request.user,
        )
        queryset = AccessControlList.objects.restrict_queryset(
            permission=permission_document_view, queryset=queryset,
            user=request.user
        )
        self.count = queryset.count()
        return super(DashboardWidgetTotalCheckouts, self).render(
            request=request
        )
