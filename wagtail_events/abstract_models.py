# -*- coding:utf8 -*-

from __future__ import unicode_literals

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import models
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.models import Page

from wagtail_events.managers import EventInstanceManager
from wagtail_events.utils import _DATE_FORMAT_RE


class AbstractPaginatedIndexPage(Page):
    """ """
    paginate_by = models.PositiveIntegerField(blank=True, null=True)
    content_panels = Page.content_panels + [FieldPanel('paginate_by')]

    class Meta(object):
        """Django model meta options."""
        abstract = True

    def _get_children(self, request):
        """
        Helper method for getting child nodes to display in the listing.

        :param request: django request
        :return: Queryset of child model instances
        """
        model_class = self.__class__.allowed_subpage_models()[0]
        children = model_class.objects.child_of(self)
        if not request.is_preview:
            children = children.filter(live=True)
        return children

    def _paginate_queryset(self, queryset, page):
        """
        Helper method for paginating the queryset provided.

        :param queryset: Queryset of model instances to paginate
        :param page: Raw page number taken from the request dict
        :return: Queryset of child model instances
        """
        paginator = Paginator(queryset, self.paginate_by)
        try:
            queryset = paginator.page(page)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)
        return queryset, paginator

    def get_context(self, request, *args, **kwargs):
        """
        Adds child pages to the context and paginates them.

        :param request: HttpRequest instance
        :param args: default positional args
        :param kwargs: default keyword args
        :return: Context data to use when rendering the template
        """
        context = super(AbstractPaginatedIndexPage, self).get_context(
            request,
            *args,
            **kwargs
        )
        queryset = self._get_children(request)
        is_paginated = False
        paginator = None

        # Paginate the child nodes if paginate_by has been specified
        if self.paginate_by:
            is_paginated = True
            queryset['items'], paginator = self._paginate_queryset(
                queryset['items'],
                request.GET.get('page')
            )

        context.update(
            children=queryset,
            paginator=paginator,
            is_paginated=is_paginated
        )
        return context


class AbstractEventIndexPage(AbstractPaginatedIndexPage):
    """ """
    class Meta(object):
        """Django model meta options."""
        abstract = True

    def get_dateformat(self):
        """Returns the dateformat."""
        return _DATE_FORMAT_RE


class AbstractEventInstance(models.Model):
    """ """
    title = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)

    class Meta(object):
        """Django model meta options."""
        abstract = True
        ordering = ['start_date']

    objects = EventInstanceManager()

    panels = [
        FieldPanel('title'),
        FieldPanel('start_date'),
        FieldPanel('end_date'),
    ]
