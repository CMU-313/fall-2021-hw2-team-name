from __future__ import unicode_literals

from django.apps import apps
from django.contrib.auth import get_user_model

from mayan.celery import app


@app.task(ignore_result=True)
def task_send_document(body, sender, subject, recipient, user_mailer_id, as_attachment=False, document_id=None, user_id=None):
    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )
    UserMailer = apps.get_model(
        app_label='mailer', model_name='UserMailer'
    )
    User = get_user_model()

    if document_id:
        document = Document.objects.get(pk=document_id)
    else:
        document = None

    user_mailer = UserMailer.objects.get(pk=user_mailer_id)
    if user_id:
        user = User.objects.get(pk=user_id)
    else:
        user = None

    user_mailer.send_document(
        as_attachment=as_attachment, body=body, document=document,
        subject=subject, to=recipient, _user=user
    )
