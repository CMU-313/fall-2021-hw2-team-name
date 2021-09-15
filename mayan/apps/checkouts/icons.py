from __future__ import absolute_import, unicode_literals

from mayan.apps.appearance.classes import Icon

icon_checkin_document = Icon(
    driver_name='fontawesome-dual', primary_symbol='shopping-cart',
    secondary_symbol='minus'
)
icon_checkout_document = Icon(
    driver_name='fontawesome-dual', primary_symbol='shopping-cart',
    secondary_symbol='plus'
)
icon_checkout_info = Icon(driver_name='fontawesome', symbol='shopping-cart')
icon_dashboard_checkouts = Icon(
    driver_name='fontawesome', symbol='shopping-cart'
)
