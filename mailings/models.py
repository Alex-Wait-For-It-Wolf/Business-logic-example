from django.db import models

class CommonMailingList(models.Model):
    """Рассылка на общие материалы с сайта"""
    email = models.EmailField('Email подписчиков')

    class Meta:
        db_table = 'common_mailing_list' # имя таблички в базе данных, в которой мы будем хранить эти данные


class CaseMailingList(models.Model):
    """Рассызка на материалы конкретного дела"""
    email = models.EmailField('Email подписчиков')
    case = models.ForeignKey(to='cases.Case', 
                             verbose_name='Дело', 
                             on_delete=models.CASCADE)

    class Meta:
        db_table = 'case_mailing_list'
