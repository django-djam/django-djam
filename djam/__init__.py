from djam.riffs.admin import admin


def autodiscover():
    from django.contrib.admin import autodiscover, site, ModelAdmin
    from djam.riffs.models import ModelRiff
    autodiscover()

    riff_classes = []
    for modeladmin in site._registry.values():
        model = modeladmin.model
        class_name = model.__name__ + str('Riff')
        if modeladmin.declared_fieldsets:
            fieldsets = modeladmin.declared_fieldsets
        elif modeladmin.exclude:
            fields = [f.name for f in modeladmin.opts.fields
                      if f.name not in modeladmin.exclude]
            fieldsets = [(None, {'fields': fields})]
        else:
            fieldsets = None
        if modeladmin.form is ModelAdmin.form:
            form_class = None
        else:
            form_class = modeladmin.form
        attrs = {
            'model': model,
            'update_kwargs': {
                'form_class': form_class,
                'fieldsets': fieldsets,
                'readonly': modeladmin.readonly_fields,
            },
        }
        if hasattr(modeladmin, 'add_form'):
            attrs['create_kwargs'] = {'form_class': modeladmin.add_form}
            if hasattr(modeladmin, 'add_fieldsets'):
                attrs['create_kwargs']['fieldsets'] = modeladmin.add_fieldsets
        else:
            attrs['create_kwargs'] = attrs['update_kwargs'].copy()
        riff_classes.append(type(class_name, (ModelRiff,), attrs))
    riff_classes.sort(key=lambda cls: cls.__name__)
    for cls in riff_classes:
        admin.register_model(cls.model, cls)
