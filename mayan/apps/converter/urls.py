from __future__ import unicode_literals

from django.conf.urls import url

from .views import (
    TransformationCreateView, TransformationDeleteView, TransformationEditView,
    TransformationListView
)

urlpatterns = [
    url(
        regex=r'^objects/(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_id>\d+)/transformations/$',
        name='transformation_list', view=TransformationListView.as_view()
    ),
    url(
        regex=r'^objects/(?P<app_label>[-\w]+)/(?P<model>[-\w]+)/(?P<object_id>\d+)/transformations/create/$',
        name='transformation_create', view=TransformationCreateView.as_view()
    ),
    url(
        regex=r'^transformations/delete/(?P<transformation_id>\d+)/$',
        name='transformation_delete', view=TransformationDeleteView.as_view()
    ),
    url(
        regex=r'^transformations/edit/(?P<transformation_id>\d+)/$',
        name='transformation_edit', view=TransformationEditView.as_view()
    ),
]
