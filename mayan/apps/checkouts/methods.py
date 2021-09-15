from __future__ import unicode_literals

from django.apps import apps


def method_check_in(self, user=None):
    DocumentCheckout = apps.get_model(
        app_label='checkouts', model_name='DocumentCheckout'
    )
    return DocumentCheckout.objects.check_in_document(
        document=self, user=user
    )


def method_get_checkout_info(self):
    DocumentCheckout = apps.get_model(
        app_label='checkouts', model_name='DocumentCheckout'
    )
    return DocumentCheckout.objects.get_document_checkout_info(document=self)


def method_get_checkout_state(self):
    DocumentCheckout = apps.get_model(
        app_label='checkouts', model_name='DocumentCheckout'
    )
    return DocumentCheckout.objects.get_document_checkout_state(document=self)


def method_is_checked_out(self):
    DocumentCheckout = apps.get_model(
        app_label='checkouts', model_name='DocumentCheckout'
    )
    return DocumentCheckout.objects.is_document_checked_out(document=self)
