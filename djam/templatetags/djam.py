from django import template
from django.conf import settings


register = template.Library()


@register.assignment_tag(takes_context=True)
def get_displayed_riffs(context, riff):
    try:
        request = context['request']
    except KeyError:
        if settings.TEMPLATE_DEBUG:
            raise
        return ''

    return [r for r in riff.riffs if not r.is_hidden(request)]

@register.simple_tag
def riff_url(riff, view_name, *args, **kwargs):
    return riff.reverse(view_name, *args, **kwargs)
