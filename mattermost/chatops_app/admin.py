from django.contrib import admin

from . import models


@admin.register(models.SlackUser)
class SlackUserAdmin(admin.ModelAdmin):
    list_display = 'name', 'id', 'slack_user_id', 'groups_list', 'allowed_commands'
    search_fields = 'name', 'slack_user_id'


@admin.register(models.ServicePermissions)
class SlackUserAdmin(admin.ModelAdmin):
    list_display = 'service', 'allowed_groups'


@admin.register(models.MgrQueue)
class MgrQueueAdmin(admin.ModelAdmin):
    list_display = 'id', 'name', 'direction', 'state', 'opened_by', 'time_opened', 'closed_by', 'time_closed', 'timer'
    search_fields = 'id', 'name', 'state', 'opened_by', 'time_opened', 'closed_by', 'time_closed'


@admin.register(models.MgrDomain)
class MgrDomainAdmin(admin.ModelAdmin):
    list_display = 'id', 'domain_id', 'name', 'queue', 'state', 'requested_by', 'processed_by'
    search_fields = 'domain_id', 'name', 'queue', 'state', 'requested_by', 'processed_by'


class StateEnumModelAdmin(admin.ModelAdmin):
    list_display = 'id', 'name'


admin.site.register((models.MgrDomainState, models.MgrQueueState), StateEnumModelAdmin)
