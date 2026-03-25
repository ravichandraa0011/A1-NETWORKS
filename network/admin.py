from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Connection, ProjectPortfolio

admin.site.register(Connection)
admin.site.register(ProjectPortfolio)