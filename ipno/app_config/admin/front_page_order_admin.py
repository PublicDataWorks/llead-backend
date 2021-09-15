from adminsortable.admin import SortableAdmin
from django.contrib import admin

from app_config.models import FrontPageOrder


admin.site.register(FrontPageOrder, SortableAdmin)
