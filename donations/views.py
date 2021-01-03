from django.shortcuts import render

from mailings.mailchimp_services import add_mailchimp_email_with_tag


def webhook(request):
    """Обработчик вебхука от платежной системы"""
    add_mailchimp_email_with_tag(email=request.POST.get('email'),
                                 audience_name='DONATES',
                                 tag='DONATE')
