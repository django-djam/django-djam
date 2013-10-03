from __future__ import absolute_import
from __future__ import unicode_literals

from django import template
from django.conf import settings
from django.forms.forms import pretty_name
from django.forms.widgets import CheckboxInput
from django.template.base import kwarg_re, TemplateSyntaxError
from django.utils.encoding import force_unicode, smart_str
from floppyforms.templatetags.floppyforms import FormRowNode

from djam.riffs.base import Riff


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


class RiffURLNode(template.Node):
    def __init__(self, riff, view_name, args, kwargs, asvar):
        self.riff = riff
        self.view_name = view_name
        self.args = args
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        args = [arg.resolve(context) for arg in self.args]
        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
                       for k, v in self.kwargs.iteritems()])
        riff = self.riff.resolve(context)
        view_name = self.view_name.resolve(context)
        url = riff.reverse(view_name, args=args, kwargs=kwargs)

        if self.asvar:
            context[self.asvar] = url
            return ''

        return url


@register.tag
def riff_url(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise TemplateSyntaxError("'{0}' takes at least two arguments: a riff "
                                  "and a view path.".format(bits[0]))

    riff = parser.compile_filter(bits[1])
    view_name = parser.compile_filter(bits[2])

    args = []
    kwargs = {}
    asvar = None
    bits = bits[3:]
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    if bits:
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to {0} tag"
                                          "".format(bits[0]))
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

    return RiffURLNode(riff, view_name, args, kwargs, asvar)


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


@register.filter
def has_add_permission(riff, request):
    if not hasattr(request, 'user') or not isinstance(riff, Riff):
        return ''
    return riff.has_add_permission(request)


@register.filter
def has_change_permission(riff, request):
    if not hasattr(request, 'user') or not isinstance(riff, Riff):
        return ''
    return riff.has_change_permission(request)


@register.filter
def has_delete_permission(riff, request):
    if not hasattr(request, 'user') or not isinstance(riff, Riff):
        return ''
    return riff.has_delete_permission(request)


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
