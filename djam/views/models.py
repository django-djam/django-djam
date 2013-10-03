from __future__ import unicode_literals

from django.contrib import messages
from django.forms.models import inlineformset_factory
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.utils.encoding import force_unicode
from django.utils.html import escape, escapejs
from django.utils.translation import ugettext_lazy as _
import floppyforms

from djam.forms import QueryForm
from djam.views.generic import ListView, CreateView, UpdateView, DeleteView


class ModelRiffMixin(object):
    template_name_suffix = None

    def get_template_names(self):
        if self.template_name:
            return [self.template_name]

        applabel = self.model._meta.app_label
        slug = self.riff.slug

        return ['djam/models/{applabel}/{modelname}/{suffix}.html'.format(suffix=self.template_name_suffix, applabel=applabel, modelname=slug),
                'djam/models/{applabel}/{suffix}.html'.format(suffix=self.template_name_suffix, applabel=applabel),
                'djam/models/{suffix}.html'.format(suffix=self.template_name_suffix)]

    def get_context_data(self, **kwargs):
        context = super(ModelRiffMixin, self).get_context_data(**kwargs)
        context.update({
            'verbose_name': self.model._meta.verbose_name,
            'verbose_name_plural': self.model._meta.verbose_name_plural,
        })
        return context


class FormsetMixin(object):
    formsets = []

    def get_formset(self, model, **kwargs):
        if self.model is not None:
            parent_model = self.model
        elif hasattr(self, 'object') and self.object is not None:
            parent_model = self.object.__class__
        else:
            parent_model = self.get_queryset().model
        if not kwargs.get('form'):
            kwargs['form'] = floppyforms.ModelForm
        if not kwargs.get('formfield_callback'):
            kwargs['formfield_callback'] = self.formfield_callback

        kwargs['fields'] = self._get_form_fields(kwargs['form'],
                                                 kwargs.pop('fieldsets'))
        kwargs['exclude'] = self._get_form_fields(kwargs['form'],
                                                  kwargs.pop('readonly'))
        cls = inlineformset_factory(parent_model, model, **kwargs)
        cls.verbose_name = model._meta.verbose_name
        cls.verbose_name_plural = model._meta.verbose_name_plural

        kwargs = {
            'instance': self.object,
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return cls(**kwargs)

    def get_formsets(self):
        return [self.get_formset(**kwargs.copy())
                for kwargs in self.formsets]

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formsets = self.get_formsets()
        context = self.get_context_data(form=form, formsets=formsets)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formsets = self.get_formsets()
        if (form.is_valid() and
                all((formset.is_valid() for formset in formsets))):
            return self.form_valid(form, formsets)
        else:
            return self.form_invalid(form, formsets)

    def form_valid(self, form, formsets):
        self.object = form.save()
        for formset in formsets:
            formset.instance = self.object
            formset.save()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formsets):
        context = self.get_context_data(form=form, formsets=formsets)
        return self.render_to_response(context)


def unicode_column(obj):
    return force_unicode(obj)
unicode_column.short_description = 'unicode'
unicode_column.do_not_call_in_templates = True


class ModelListView(ModelRiffMixin, ListView):
    template_name_suffix = 'list'
    columns = (unicode_column,)
    link_columns = None
    per_page = 100
    filters = None
    search = None
    #: May be a list of fields to use to order the list. Currently
    #: only the first field will actually be used.
    order = None

    def dispatch(self, request, *args, **kwargs):
        if not self.riff.has_change_permission(request):
            raise Http404
        return super(ModelListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(ModelListView, self).get_queryset()
        data = self.request.GET.copy()
        if 'order' not in data:
            order = self.order or self.model._meta.ordering
            if order:
                data['order'] = order[0]
        self.form = QueryForm(queryset, self.filters, self.columns,
                              self.search, data=data)
        return self.form.get_queryset()

    def get_context_data(self, **kwargs):
        context = super(ModelListView, self).get_context_data(**kwargs)
        context.update({
            'columns': self.columns,
            'link_columns': self.link_columns or self.columns[:1],
            'query_form': self.form,
        })
        return context


class ModelCreateView(ModelRiffMixin, FormsetMixin, CreateView):
    template_name_suffix = 'create'

    def dispatch(self, request, *args, **kwargs):
        if not self.riff.has_add_permission(request):
            raise Http404
        return super(ModelCreateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = None
        return super(ModelCreateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        return super(ModelCreateView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        if self.riff.has_change_permission(self.request):
            return self.riff.reverse('update', kwargs={'pk': self.object.pk})
        return self.riff.base_riff.get_default_url()

    def form_valid(self, form, formsets):
        response = super(ModelCreateView, self).form_valid(form, formsets)
        if self.request.GET.get('is_popup'):
            return HttpResponse(
                '<!DOCTYPE html><html><head><title></title></head><body>'
                '<script type="text/javascript">opener.djam.finishAdd'
                '(window, "{0}", "{1}");</script></body></html>'.format(
                    escape(form.instance.pk), escapejs(form.instance)))
        msg_kwargs = {
            'name': force_unicode(self.model._meta.verbose_name),
            'obj': force_unicode(self.object),
        }
        msg = _('The {name} "{obj}" was added successfully. '
                'You may edit it again below.'.format(**msg_kwargs))
        messages.success(self.request, msg)
        return response

    def get_crumbs(self):
        crumbs = super(ModelCreateView, self).get_crumbs()
        crumbs += [(None, _('Add a {0}'.format(self.model._meta.verbose_name)))]
        return crumbs


class ModelUpdateView(ModelRiffMixin, FormsetMixin, UpdateView):
    template_name_suffix = 'update'

    def dispatch(self, request, *args, **kwargs):
        if not self.riff.has_change_permission(request):
            raise Http404
        return super(ModelUpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(ModelUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(ModelUpdateView, self).post(request, *args, **kwargs)

    def get_success_url(self):
        return self.riff.reverse('update', kwargs={'pk': self.object.pk})

    def form_valid(self, form, formsets):
        msg_kwargs = {
            'name': force_unicode(self.model._meta.verbose_name),
            'obj': force_unicode(self.object),
        }
        msg = _('The {name} "{obj}" was updated successfully. You may edit '
                'it again below.'.format(**msg_kwargs))
        messages.success(self.request, msg)
        return super(ModelUpdateView, self).form_valid(form, formsets)

    def get_crumbs(self):
        crumbs = super(ModelUpdateView, self).get_crumbs()
        crumbs += [
            (self.riff.reverse('update', kwargs={'pk': self.object.pk}),
             unicode(self.object)),
        ]
        return crumbs


class ModelDeleteView(ModelRiffMixin, DeleteView):
    template_name_suffix = 'delete'

    def dispatch(self, request, *args, **kwargs):
        if not self.riff.has_delete_permission(request):
            raise Http404
        return super(ModelDeleteView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.riff.has_change_permission(self.request):
            return self.riff.get_default_url()
        return self.riff.base_riff.get_default_url()

    def delete(self, *args, **kwargs):
        response = super(ModelDeleteView, self).delete(*args, **kwargs)
        msg_kwargs = {
            'name': force_unicode(self.model._meta.verbose_name),
            'obj': force_unicode(self.object),
        }
        msg = _('The {name} "{obj}" was deleted successfully.'
                ''.format(**msg_kwargs))
        messages.success(self.request, msg)
        return response

    def get_crumbs(self):
        crumbs = super(ModelDeleteView, self).get_crumbs()
        crumbs += [(None, _('Delete {0}'.format(unicode(self.object))))]
        return crumbs
