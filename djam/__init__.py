from djam.riffs.admin import admin


def autodiscover():
    from django.contrib.admin import autodiscover, site
    from djam.riffs.models import ModelRiff
    autodiscover()

    for modeladmin in site._registry.values():
        model = modeladmin.model
        class_name = model.__name__ + str('Riff')
        attrs = {
            'model': model,
            'update_form_class': modeladmin.form,
            'update_form_fields': modeladmin.fields,
            'update_form_exclude': modeladmin.exclude,
            'create_form_class': getattr(modeladmin, 'add_form', None),
        }
        riff_class = type(class_name, (ModelRiff,), attrs)
        admin.register_model(model, riff_class)
