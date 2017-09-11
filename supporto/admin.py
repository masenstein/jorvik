from django.contrib import admin
from supporto.models import KBCache
from gruppi.readonly_admin import ReadonlyAdminMixin


class AdminKBCache(ReadonlyAdminMixin, admin.ModelAdmin):
    search_fields = ['articleid','subject']
    list_display = ('articleid', 'subject', 'dateline', 'viewcount', 'lastupdate', )

admin.site.register(KBCache, AdminKBCache)