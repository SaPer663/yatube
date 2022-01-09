from django.conf import settings
from django.core.paginator import Paginator


def create_paginator(request, obj_list, per_page=settings.ITEMS_PER_PAGE):
    """Возвращает паджинатор.
    Принимает обязательные объект request и список объектов, которые нужно
    пропаджинировать.
    Необязательный аргумент per_page: int указывает количество объектов не
    странице. По умолчанию равно переменной settings.ITEMS_PER_PAGE.
    """
    paginator = Paginator(obj_list, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
