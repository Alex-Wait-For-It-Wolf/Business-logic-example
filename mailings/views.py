from typing import Optional

from mailchimp3 import MailChimp

from django.http import JsonResponse
from django.conf import settings

from cases.models import Case
from .models import CommonMailingList, CaseMailingList


# Способ 1: Как писать views (как не нужно делать)

def add_to_common_list_view(request):
    """Веб-сервис, добавляющий email в общий лист рассылки"""

    email = request.GET.get('email')
    if not email:
        return JsonResponse({'success': False, 'message': 'Передайте email'})

    mailchimp_client = MailChimp(
        mc_api=settings.MAILCHIMP_API_KEY,
        mc_user=settings.MAILCHIMP_USERNAME)
    mailchimp_client.lists.members.create(settings.MAILCHIMP_COMMON_LIST_ID, {
        'email_address': email,
        'status': 'subscribed',
    })
    subscriber_hash = mailchimp_client \
        .search_members \
        .get(query=email
             fields='exact_matches.members.id') \
        .get('exact_matches').get('members')[0].get('id')
    mailchimp_client.lists.members.tags.update(
        list_id=settings.MAILCHIMP_COMMON_LIST_ID,
        subscriber_hash=subscriber_hash,
        data={'tags': [{'name': 'COMMON TAG', 'status': 'activate'}]})

    CommonMailingList.objects.get_or_create(email=email)

    return JsonResponse({'success': True})


def add_to_case_list_view(request):
    """Веб-сервис, добавляющий email в лист рассылки по конкретному делу"""

    email = request.GET.get('email')
    if not email:
        return JsonResponse({'success': False, 'message': 'Передайте email'})
    case_id = request.GET.get('case_id')
    if not case_id:
        return JsonResponse({'success': False, 'message': 'Передайте case_id'})

    mailchimp_client = MailChimp(
        mc_api=settings.MAILCHIMP_API_KEY,
        mc_user=settings.MAILCHIMP_USERNAME)
    mailchimp_client.lists.members.create(settings.MAILCHIMP_CASE_LIST_ID, {
        'email_address': email,
        'status': 'subscribed',
    })
    subscriber_hash = mailchimp_client \
        .search_members \
        .get(query=email
             fields='exact_matches.members.id') \
        .get('exact_matches').get('members')[0].get('id')

    case = Case.objects.get(pk=case_id)
    case_tag = f'Case {case.name}'

    mailchimp_client.lists.members.tags.update(
        list_id=settings.MAILCHIMP_CASE_LIST_ID,
        subscriber_hash=subscriber_hash,
        data={'tags': [{'name': case_tag, 'status': 'activate'}]})

    CaseMailingList.objects.get_or_create(email=email)

    return JsonResponse({'success': True})


# Способ 2: Рефактореные views (лучше чем Способ 1, но можно еще лучше)

def add_to_common_list_view(request):
    """Веб-сервис, добавляющий email в общий лист рассылки"""

    email = request.GET.get('email')
    if not email:
        return JsonResponse({'success': False, 'message': 'Передайте email'})

    _add_mailchimp_email_with_tag(audience_id=settings.MAILCHIMP_COMMON_LIST_ID,
                                  email=email,
                                  tag='COMMON TAG')

    CommonMailingList.objects.get_or_create(email=email)

    return JsonResponse({'success': True})

def add_to_case_list_view(request):
    """Веб-сервис, добавляющий email в лист рассылок по конкретному делу"""

    email = request.GET.get('email')
    if not email:
        return JsonResponse({'success': False, 'message': 'Передайте email'})
    case_id = request.GET.get('case_id')
    if not case_id:
        return JsonResponse({'success': False, 'message': 'Передайте case_id'})

    case = Case.objects.get(pk=case_id)
    case_tag = f'Case {case.name}'
    _add_mailchimp_email_with_tag(audience_id=settings.MAILCHIMP_CASE_LIST_ID,
                                  email=email,
                                  tag=case_tag)
    CaseMailingList.objects.get_or_create(email=email, case=case)

    return JsonResponse({'success': True})


def _get_mailchimp_client() -> MailChimp:
    """Возвращает клиент API для работы с Mailchimp"""
    return MailChimp(
        mc_api=settings.MAILCHIMP_API_KEY,
        mc_user=settings.MAILCHIMP_USERNAME)


def _add_email_to_mailchimp_audience(audience_id: str, email: str) -> None:
    """Добавляет email в Mailchimp аудиторию с идентификатором audience_id"""
    _get_mailchimp_client().lists.members.create(audience_id, {
        'email_address': email,
        'status': 'subscribed'
    })


def _get_mailchimp_subscriber_hash(email: str) -> Optional[str]:
    """Возвращает идентификатор email'а в Mailchimp или None,
       если email там не найден"""
    members = _get_mailchimp_client() \
        .search_members \
        .get(query=email,
             fields='exact_matches.members.id') \
        .get('exact_matches').get('members')
    if not members:
        return None
    return members[0].get('id')


def _add_mailchimp_tag(audience_id: str, subscriber_hash: str, tag: str) -> None:
    """Добавляет тен tag для email'а с идентификатором subscriber_hash
       в аудитории audience_id"""
    _get_mailchimp_client().lists.members.tags.update(
        list_id=audience_id,
        subscriber_hash=subscriber_hash,
        data={'tags': [{'name': tag, 'status': 'activate'}]})

def _add_mailchimp_email_with_tag(audience_id: str, email: str) -> None:
    _add_email_to_mailchimp_audience(audience_id=audience_id,
                                     email=email)
    _add_mailchimp_tag(audience_id=audience_id,
                       subscriber_hash=_get_mailchimp_subscriber_hash(email),
                       tag=tag)

# Способ 3: Вынос бизнес-логики в отдельный файл (если её не много) либо в отдельный Python package (если её много) (самый оптимальный способ)
# Чтобы в PyCharm создать Python Package нужно ПКМ на папке, выбрать New и далее выбрать Python Package.
# Бищнес-логику обычно принято называть Сервисы Services, и помещать в тот app (например mailings) к которому она принадлежит, и если нужно создать сервисы под конкретный функционал, их так и называют - пример mailchimp_services.py, а если это Python Package, тогда он так и называется services, а внутри него уже нужные модули. 

def add_email_to_common_mailchimp_list_view(request):
    """Веб-сервис, добавляющий email в общий лист рассылки"""

    email = request.GET.get('email')
    if not email:
        return JsonResponse({'success': False, 'message': 'Передайте email'})
    add_email_to_common_mailchimp_list(email=email)
    return JsonResponse({'success': True})


def add_email_to_case_mailchimp_list_view(request):
    """Веб-сервис, добавляющий email в лист рассылки по конкретному делу"""

    email = request.GET.get('email')
    if not email:
        return JsonResponse({'success': False, 'message': 'Передайте email'})
    if not case_id:
        return JsonResponse({'success': False, 'message': 'Передайте case_id'})
    add_email_to_case_mailchimp_list(email=email, case_id=case_id)

    return JsonResponse({'success': True})
