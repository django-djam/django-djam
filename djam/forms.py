import operator

from django.contrib.admin.util import lookup_needs_distinct
from django.db import models
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _
import floppyforms as forms


def _search_lookup(field):
    # returns a lookup for searching a database field based
    # on a shortcut name.
    if field[0] in ('^', '=', '@'):
        if field.startswith('^'):
            lookup = 'istartswith'
        elif field.startswith('='):
            lookup = 'iexact'
        elif field.startswith('@'):
            lookup = 'icontains'
        field = field[1:]
    else:
        lookup = 'icontains'
    return "{0}__{1}".format(field, lookup)


def _reverse_order(order):
    if not isinstance(order, basestring):
        raise ValueError
    if order[0] == '-':
        return order[1:]
    else:
        return '-' + order


class FilterField(forms.TypedChoiceField):
    requires_distinct = False

    def __init__(self, model, field_name, *args, **kwargs):
        self.model = model
        self.field_name = field_name
        self.field = self.model._meta.get_field(self.field_name)
        super(FilterField, self).__init__(choices=self.get_choices(), *args, **kwargs)

    def get_choices(self):
        raise NotImplementedError

    def filter(self, queryset, value):
        raise NotImplementedError


class BooleanFilterField(FilterField):
    def get_choices(self):
        return (
            ('', _('All')),
            ('1', _('Yes')),
            ('0', _('No')),
        )

    def filter(self, queryset, value):
        if value == '1':
            return queryset.filter(**{self.field_name: True})
        elif value == '0':
            return queryset.filter(**{self.field_name: False})
        else:
            return queryset


class SimpleFilterField(FilterField):
    EMPTY_VALUE = ''

    def __init__(self, *args, **kwargs):
        super(SimpleFilterField, self).__init__(*args, **kwargs)
        self.requires_distinct = isinstance(self.field, models.ManyToManyField)

    def get_choices(self):
        return ((self.EMPTY_VALUE, _('All')),) + tuple(self.field.choices)

    def filter(self, queryset, value):
        if value == self.EMPTY_VALUE:
            return queryset
        return queryset.filter(**{self.field_name: value})


# ordering should be passed in as initial['order'].
class QueryForm(forms.Form):
    model_field_filters = {
        models.BooleanField: BooleanFilterField,
        models.NullBooleanField: BooleanFilterField,
    }

    def __init__(self, queryset, filters, columns, search,
                 *args, **kwargs):
        super(QueryForm, self).__init__(*args, **kwargs)
        self.model = queryset.model
        self.queryset = queryset.all()
        self.columns = columns
        # Records whether this instance needs to use a distinct query
        self.use_distinct = False

        if columns:
            self.order_fields = {}
            for column in columns:
                if isinstance(column, basestring):
                    order = force_unicode(column)
                    try:
                        self.model._meta.get_field(column)
                    except models.FieldDoesNotExist:
                        if (hasattr(self.model, column) and
                            hasattr(column, 'admin_order_field')):
                            order = column.admin_order_field
                        else:
                            continue
                elif hasattr(column, 'admin_order_field'):
                    order = column.admin_order_field
                else:
                    continue
                self.order_fields[column] = order
            if self.order_fields:
                choices = reduce(operator.add,
                                 (((f, f), (_reverse_order(f), _reverse_order(f)))
                                  for f in self.order_fields.itervalues()))
                self.fields['order'] = forms.MultipleChoiceField(choices=choices, required=False)

        self.search = search
        if search:
            self.fields['search'] = forms.CharField(required=False)

        self.filters = filters
        if filters:
            if 'search' in filters or 'order' in filters:
                raise ValueError("'search' and 'order' can't be used as filter names.")
            for f in filters:
                if isinstance(f, basestring):
                    model_field = self.model._meta.get_field(f).__class__
                    if model_field in self.model_field_filters:
                        field_class = self.model_field_filters[model_field]
                    else:
                        field_class = SimpleFilterField
                    field = field_class(self.model, f, required=False)
                else:
                    field = f
                if getattr(field, 'requires_distinct', False):
                    self.use_distinct = True
                self.fields[f] = field

    def has_filters(self):
        return bool(set(self.fields) - set(('search', 'order')))

    def get_queryset(self):
        if not self.is_valid():
            return self.queryset

        queryset = self._filter(self.queryset)
        queryset = self._order(queryset)
        queryset = self._select_related(queryset)
        queryset = self._search(queryset)

        if self.use_distinct:
            queryset = queryset.distinct()

        return queryset

    def _order(self, queryset):
        if 'order' in self.cleaned_data:
            orders = []
            # Ensure a deterministic order by pk if it's not already in the mix.
            pk_name = self.model._meta.pk.name
            if not set(orders) & set(['pk', '-pk', pk_name, '-' + pk_name]):
                orders.append('-pk')
            queryset = queryset.order_by(*orders)
        return queryset

    def _filter(self, queryset):
        for name, field in self.fields.iteritems():
            if name in ('search', 'order'):
                continue

            queryset = field.filter(queryset, self.cleaned_data[name])

        return queryset

    def _search(self, queryset):
        if 'search' in self.cleaned_data:
            lookups = [_search_lookup(str(field))
                       for field in self.search]
            for bit in self.cleaned_data['search'].split():
                qlist = [models.Q(**{lookup: bit})
                         for lookup in lookups]
                queryset = queryset.filter(reduce(operator.or_, qlist))
            if not self.use_distinct:
                for lookup in lookups:
                    if lookup_needs_distinct(self.model._meta, lookup):
                        self.use_distinct = True
                        break
        return queryset

    def _select_related(self, queryset):
        # If the queryset doesn't already have select_related defined,
        # check the columns used to auto-select ManyToOne rels that
        # will be used.
        if not queryset.query.select_related:
            related = []
            for field_name in self.columns:
                try:
                    field = self.model._meta.get_field(field_name)
                except models.FieldDoesNotExist:
                    pass
                else:
                    if isinstance(field.rel, models.ManyToOneRel):
                        related.append(field_name)
            if related:
                queryset = queryset.select_related(*related)
        return queryset
