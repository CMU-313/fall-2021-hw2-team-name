class ObjectCopyViewTestMixin:
    def _request_object_copy_view(self):
        return self.post(
            kwargs=self.test_object_view_kwargs, viewname='common:object_copy'
        )
