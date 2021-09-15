from __future__ import unicode_literals

import json

from ..models import UserMailer

from .literals import (
    TEST_EMAIL_ADDRESS, TEST_EMAIL_FROM_ADDRESS, TEST_USER_MAILER_BACKEND_PATH,
    TEST_USER_MAILER_LABEL, TEST_USER_MAILER_LABEL_EDITED
)


class MailerTestMixin(object):
    def _create_user_mailer(self):
        self.user_mailer = UserMailer.objects.create(
            default=True,
            enabled=True,
            label=TEST_USER_MAILER_LABEL,
            backend_path=TEST_USER_MAILER_BACKEND_PATH,
            backend_data=json.dumps(
                {
                    'from': TEST_EMAIL_FROM_ADDRESS
                }
            )
        )

    def _request_test_user_mailer_create(self):
        return self.post(
            viewname='mailer:user_mailer_create', kwargs={
                'class_path': TEST_USER_MAILER_BACKEND_PATH
            }, data={
                'default': True, 'enabled': True,
                'label': TEST_USER_MAILER_LABEL,
            }
        )

    def _request_test_user_mailer_delete(self):
        return self.post(
            viewname='mailer:user_mailer_delete',
            kwargs={'mailer_id': self.user_mailer.pk}
        )

    def _request_test_user_mailer_edit(self):
        return self.post(
            viewname='mailer:user_mailer_edit',
            kwargs={'mailer_id': self.user_mailer.pk},
            data={
                'label': TEST_USER_MAILER_LABEL_EDITED
            }
        )

    def _request_test_user_mailer_list_view(self):
        return self.get(viewname='mailer:user_mailer_list')

    def _request_test_user_mailer_test(self):
        return self.post(
            viewname='mailer:user_mailer_test',
            kwargs={'mailer_id': self.user_mailer.pk},
            data={
                'email': getattr(
                    self, 'test_email_address', TEST_EMAIL_ADDRESS
                )
            }
        )
