from django.contrib import admin

from test_project.example_app.models import ExampleModel


class ExampleModelAdmin(admin.ModelAdmin):
    pass


admin.site.register(ExampleModel, ExampleModelAdmin)
