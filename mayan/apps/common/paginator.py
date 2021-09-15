from __future__ import absolute_import, unicode_literals

from pure_pagination import Paginator
from pure_pagination.paginator import Page, PageRepresentation


class PurePage(Page):
    """
    Subclass of pure_pagination Page class to support configurable page
    querystring keys
    """
    def __init__(self, object_list, number, paginator, page_kwarg='page'):
        self.object_list = object_list
        self.page_kwarg = page_kwarg
        self.paginator = paginator
        if paginator.request:
            # Reason: I just want to perform this operation once, and not once per page
            self.base_queryset = self.paginator.request.GET.copy()
            # self.base_queryset['page'] = 'page'
            # self.base_queryset = self.base_queryset.urlencode().replace(
            # '%', '%%').replace('page=page', 'page=%s')

        self.number = PageRepresentation(number, self._other_page_querystring(number))

    def _other_page_querystring(self, page_number):
        """
        Returns a query string for the given page, preserving any
        GET parameters present.
        """
        if self.paginator.request:
            self.base_queryset[self.page_kwarg] = page_number
            return self.base_queryset.urlencode()

        # raise Warning("You must supply Paginator() with the request object
        # for a proper querystring.")
        return '{}={}'.format(self.page_kwarg, page_number)


class PurePaginator(Paginator):
    """
    Subclass of pure_pagination Paaginator class to support configurable page
    querystring keys
    """
    page_class = PurePage

    def __init__(self, object_list, per_page, allow_empty_first_page=True, orphans=0, page_kwarg='page', request=None):
        self._num_pages = self._count = None
        self.allow_empty_first_page = allow_empty_first_page
        self.object_list = object_list
        self.orphans = orphans
        self.per_page = per_page
        self.page_kwarg = page_kwarg
        self.request = request

    def page(self, number):
        """
        Returns a Page object for the given 1-based page number.
        """
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count

        return self.page_class(
            object_list=self.object_list[bottom:top], number=number,
            paginator=self, page_kwarg=self.page_kwarg
        )
