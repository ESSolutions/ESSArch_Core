from django.contrib import admin

from ESSArch_Core.tags.models import (
    NodeRelationType,
    StructureType,
    StructureUnitType,
    TagVersionType,
)


class NodeRelationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'mirrored_type')


class StructureUnitTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'structure_type')


class TagVersionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'archive_type')


admin.site.register(NodeRelationType, NodeRelationTypeAdmin)
admin.site.register(StructureType)
admin.site.register(StructureUnitType, StructureUnitTypeAdmin)
admin.site.register(TagVersionType, TagVersionTypeAdmin)
