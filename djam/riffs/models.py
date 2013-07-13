from __future__ import unicode_literals

from django.conf.urls.defaults import patterns, url
from django.contrib.admin import ModelAdmin, site
from django.core.exceptions import ImproperlyConfigured
from django.db.models import FieldDoesNotExist
from django.template.defaultfilters import capfirst

from djam.riffs.base import Riff
from djam.views.models import (ModelListView, ModelCreateView, ModelUpdateView,
                               ModelDeleteView, unicode_column)


def _modeladmin_fieldsets(modeladmin):
    if modeladmin.fieldsets:
        return modeladmin.fieldsets
    if modeladmin.fields:
        return [(None, {'fields': modeladmin.fields})]
    if modeladmin.exclude:
        fields = [f.name for f in modeladmin.model._meta.fields
                  if f.name not in modeladmin.exclude]
        return [(None, {'fields': fields})]
    return None


def _modeladmin_form_class(modeladmin):
    if modeladmin.form is not ModelAdmin.form:
        return modeladmin.form
    return None


class ModelRiffMetaclass(type):
    def __new__(cls, name, bases, attrs):
        model = attrs['model']
        use_modeladmin = attrs.get('use_modeladmin', True)
        new_attrs = {}
        if use_modeladmin and model in site._registry:
            modeladmin = site._registry[model]
            # Calculate new "base" attrs from modeladmin.
            fieldsets = _modeladmin_fieldsets(modeladmin)
            form_class = _modeladmin_form_class(modeladmin)
            columns = []
            for column in modeladmin.list_display:
                if column in ('__unicode__', '__str__'):
                    columns.append(unicode_column)
                else:
                    try:
                        model._meta.get_field(column)
                    except FieldDoesNotExist:
                        if hasattr(modeladmin, column):
                            columns.append(getattr(modeladmin, column))
                        elif hasattr(model, column):
                            columns.append(getattr(model, column))
                    else:
                        columns.append(column)
            new_attrs = {
                'model': model,
                'update_kwargs': {
                    'form_class': form_class,
                    'fieldsets': fieldsets,
                    'readonly': modeladmin.readonly_fields,
                    'formsets': [
                        {
                            'model': inline.model,
                            'fk_name': inline.fk_name,
                            'formset': inline.formset,
                            'form': _modeladmin_form_class(inline),
                            'extra': inline.extra,
                            'max_num': inline.max_num,
                            'can_delete': inline.can_delete,
                            'fieldsets': _modeladmin_fieldsets(inline),
                            'readonly': inline.readonly_fields,
                        }
                    for inline in modeladmin.inlines]
                },
                'list_kwargs': {
                    'columns': columns,
                    'link_columns': modeladmin.list_display_links,
                    'filters': modeladmin.list_filter,
                    'search': modeladmin.search_fields,
                    'per_page': modeladmin.list_per_page,
                    'order': modeladmin.ordering or None,
                }
            }
            for column in new_attrs['list_kwargs']['columns']:
                if callable('column'):
                    column.do_not_call_in_templates = True
            if hasattr(modeladmin, 'add_form'):
                new_attrs['create_kwargs'] = {'form_class': modeladmin.add_form}
                if hasattr(modeladmin, 'add_fieldsets'):
                    new_attrs['create_kwargs']['fieldsets'] = modeladmin.add_fieldsets
            else:
                new_attrs['create_kwargs'] = new_attrs['update_kwargs'].copy()

        # Update new_attrs from declared attrs - override "inherited" values.
        new_attrs.update(attrs)
        return super(ModelRiffMetaclass, cls).__new__(cls, name, bases, new_attrs)


class ModelRiff(Riff):
    __metaclass__ = ModelRiffMetaclass

    model = None
    list_view = ModelListView
    create_view = ModelCreateView
    update_view = ModelUpdateView
    delete_view = ModelDeleteView
    widget_template = 'djam/models/_widget.html'

    # create and update kwargs can contain:
    # - form_class
    # - fieldsets
    # - readonly
    update_kwargs = {}
    create_kwargs = {}

    # list kwargs can contain:
    # - columns
    # - link_columns
    # - filters
    # - search
    # - per_page
    # - order
    list_kwargs = {}

    def __init__(self, *args, **kwargs):
        if not self.model:
            raise ImproperlyConfigured('Please specify a model')
        if self.display_name is None:
            self.display_name = capfirst(self.model._meta.verbose_name_plural)
        if self.slug is None:
            self.slug = self.model._meta.module_name
        if self.namespace is None:
            self.namespace = '{appname}_{modelname}'.format(
                appname=self.model._meta.app_label,
                modelname=self.model._meta.module_name)
        super(ModelRiff, self).__init__(*args, **kwargs)

    def get_extra_urls(self):
        return patterns('',
            url(r'^$',
                self.wrap_view(self.list_view.as_view(**self.get_list_kwargs())),
                name='list'),
            url(r'^add/$',
                self.wrap_view(self.create_view.as_view(**self.get_create_kwargs())),
                name='create'),
            url(r'^(?P<pk>\w+)/$',
                self.wrap_view(self.update_view.as_view(**self.get_update_kwargs())),
                name='update'),
            url(r'^(?P<pk>\w+)/delete/$',
                self.wrap_view(self.delete_view.as_view(**self.get_view_kwargs())),
                name='delete'),
        )

    def get_default_url(self):
        return self.reverse('list')

    def get_view_kwargs(self):
        kwargs = super(ModelRiff, self).get_view_kwargs()
        kwargs['model'] = self.model
        return kwargs

    def get_list_kwargs(self):
        kwargs = self.get_view_kwargs()
        kwargs.update(self.list_kwargs)
        return kwargs

    def get_update_kwargs(self):
        kwargs = self.get_view_kwargs()
        kwargs.update(self.update_kwargs)
        return kwargs

    def get_create_kwargs(self):
        kwargs = self.get_view_kwargs()
        kwargs.update(self.create_kwargs)
        return kwargs

    def has_add_permission(self, request):
        opts = self.model._meta
        return request.user.has_perm(opts.app_label + '.' + opts.get_add_permission())

    def has_change_permission(self, request):
        opts = self.model._meta
        return request.user.has_perm(opts.app_label + '.' + opts.get_change_permission())

    def has_delete_permission(self, request):
        opts = self.model._meta
        return request.user.has_perm(opts.app_label + '.' + opts.get_delete_permission())

    def has_permission(self, request):
        return (self.has_add_permission(request) or
                self.has_change_permission(request))
