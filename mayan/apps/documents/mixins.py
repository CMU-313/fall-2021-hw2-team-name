from __future__ import absolute_import, unicode_literals


class RecentDocumentMixin(object):
    def dispatch(self, request, *args, **kwargs):
        result = super(RecentDocumentMixin, self).dispatch(
            request=request, *args, **kwargs
        )
        self.get_recent_document().add_as_recent_document_for_user(
            user=request.user
        )
        return result

    def get_recent_document(self):
        return self.object
