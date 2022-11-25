from django.conf import settings
from django.core.paginator import Paginator


def paginator_get_page(posts, request):
    paginator = Paginator(posts, settings.PAGE_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
