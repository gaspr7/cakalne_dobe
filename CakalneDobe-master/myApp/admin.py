from django.contrib import admin
from .models import CakDobe, importedFiles
# Register your models here.

admin.site.register(importedFiles)

@admin.register(CakDobe)
class CakDobeAdmin(admin.ModelAdmin):
    list_display=CakDobe.DisplayFields
