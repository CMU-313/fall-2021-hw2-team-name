from __future__ import unicode_literals

from django.conf.urls import url

from .views import (
    MayanLoginView, MayanLogoutView, MayanPasswordChangeDoneView,
    MayanPasswordChangeView, MayanPasswordResetCompleteView,
    MayanPasswordResetConfirmView, MayanPasswordResetDoneView,
    MayanPasswordResetView
)


urlpatterns = [
    url(regex=r'^login/$', name='login_view', view=MayanLoginView.as_view()),
    url(
        regex=r'^logout/$', name='logout_view', view=MayanLogoutView.as_view()
    ),
    url(
        regex=r'^password/change/$', name='password_change_view',
        view=MayanPasswordChangeView.as_view()
    ),
    url(
        regex=r'^password/change/done/$', name='password_change_done',
        view=MayanPasswordChangeDoneView.as_view()
    ),
    url(
        regex=r'^password/reset/$', name='password_reset_view',
        view=MayanPasswordResetView.as_view()
    ),
    url(
        regex=r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        name='password_reset_confirm_view',
        view=MayanPasswordResetConfirmView.as_view()
    ),
    url(
        regex=r'^password/reset/complete/$',
        name='password_reset_complete_view',
        view=MayanPasswordResetCompleteView.as_view()
    ),
    url(
        regex=r'^password/reset/done/$', name='password_reset_done_view',
        view=MayanPasswordResetDoneView.as_view()
    ),
]
