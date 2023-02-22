from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.db import transaction
from django.forms import Media

from mapbox_location_field.models import AddressAutoHiddenField, LocationField
from mapbox_location_field.widgets import AddressHiddenAdminInput, MapAdminInput

from departments.models import Department, OfficerMovement, WrglFile
from departments.tasks import rebuild_department_index
from news_articles.models import MatchedSentence, NewsArticle


class DepartmentAdmin(ModelAdmin):
    list_display = ("id", "agency_name", "aliases", "created_at", "updated_at")
    search_fields = (
        "agency_slug",
        "agency_name",
    )
    filter_horizontal = (
        "starred_officers",
        "starred_news_articles",
        "starred_documents",
    )

    change_form_template = "mapbox_location_field/admin_change.html"
    formfield_overrides = {
        LocationField: {"widget": MapAdminInput},
        AddressAutoHiddenField: {
            "widget": AddressHiddenAdminInput,
        },
    }

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if change:
            transaction.on_commit(lambda: rebuild_department_index(obj.id))

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """add media that is placed below form as separate argument in context"""
        extra_context = extra_context or {}
        extra_context["bottom_media"] = Media(
            js=(
                "mapbox_location_field/js/map_input.js",
                "mapbox_location_field/js/address_input.js",
            )
        )
        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    def add_view(self, request, form_url="", extra_context=None):
        """add media that is placed below form as separate argument in context"""
        extra_context = extra_context or {}
        extra_context["bottom_media"] = Media(
            js=(
                "mapbox_location_field/js/map_input.js",
                "mapbox_location_field/js/address_input.js",
            )
        )
        return super().add_view(
            request,
            form_url,
            extra_context=extra_context,
        )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "starred_officers":
            kwargs["queryset"] = request.officers
        elif db_field.name == "starred_news_articles":
            matched_sentences = MatchedSentence.objects.filter(
                officers__in=request.officers
            ).all()
            kwargs["queryset"] = NewsArticle.objects.filter(
                matched_sentences__in=matched_sentences
            ).distinct()
        elif db_field.name == "starred_documents":
            kwargs["queryset"] = request._obj_.documents.order_by("id").distinct().all()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        officers = obj.officers.order_by("id").distinct().all()

        request.officers = officers
        return super(DepartmentAdmin, self).get_form(request, obj, **kwargs)


class WrglFileAdmin(ModelAdmin):
    list_display = ("id", "slug", "name", "created_at", "updated_at")
    search_fields = (
        "slug",
        "name",
    )


class OfficerMovementAdmin(ModelAdmin):
    list_display = ("id", "start_department", "end_department", "officer")


admin.site.register(Department, DepartmentAdmin)
admin.site.register(WrglFile, WrglFileAdmin)
admin.site.register(OfficerMovement, OfficerMovementAdmin)
