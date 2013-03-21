from __future__ import unicode_literals

from django import template
from django.conf import settings
from django.forms.forms import pretty_name
from django.forms.widgets import CheckboxInput
from django.utils.encoding import force_unicode
from floppyforms.templatetags.floppyforms import FormRowNode


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


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, CheckboxInput)


@register.filter
def column(col, obj=None):
    if obj is None:
        if isinstance(col, basestring):
            header = col
        else:
            try:
                header = getattr(col, 'short_description', col.__name__)
            except AttributeError:
                header = force_unicode(col)
        return pretty_name(header)
    else:
        if isinstance(col, basestring):
            try:
                value = getattr(obj, col)
            except AttributeError:
                value = ''
            if callable(value):
                try:
                    value = value()
                except TypeError:
                    value = ''
        elif callable(col):
            try:
                value = col(obj)
            except TypeError:
                value = ''
        else:
            value = ''
        return value


@register.filter
def order(column, form):
    try:
        return form.order_fields[column]
    except (KeyError, AttributeError):
        return ''


class FieldsetNode(FormRowNode):
    def get_extra_context(self, context):
        extra_context = super(FieldsetNode, self).get_extra_context(context)
        try:
            form = context['form']
        except KeyError:
            pass
        else:
            extra_context[self.single_template_var] = form[extra_context[self.single_template_var]]

            if self.list_template_var:
                extra_context[self.list_template_var] = [form[name] for name in extra_context[self.list_template_var]]

        return extra_context


register.tag('fieldsetrow', FieldsetNode.parse)
