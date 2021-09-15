from __future__ import unicode_literals

from ..models import Message

from .literals import (
    TEST_MESSAGE_LABEL, TEST_MESSAGE_LABEL_EDITED, TEST_MESSAGE_TEXT,
    TEST_MESSAGE_TEXT_EDITED
)


class MOTDTestMixin(object):
    def _create_test_message(self):
        self.test_message = Message.objects.create(
            label=TEST_MESSAGE_LABEL, message=TEST_MESSAGE_TEXT
        )

    def _request_message_create_view(self):
        return self.post(
            viewname='motd:message_create', data={
                'label': TEST_MESSAGE_LABEL, 'message': TEST_MESSAGE_TEXT
            }
        )

    def _request_message_delete_view(self):
        return self.post(
            viewname='motd:message_delete',
            kwargs={'message_id': self.test_message.pk}
        )

    def _request_message_edit_view(self):
        return self.post(
            viewname='motd:message_edit',
            kwargs={'message_id': self.test_message.pk},
            data={
                'label': TEST_MESSAGE_LABEL_EDITED,
                'message': TEST_MESSAGE_TEXT_EDITED
            }
        )

    def _request_message_list_view(self):
        return self.get(viewname='motd:message_list')
