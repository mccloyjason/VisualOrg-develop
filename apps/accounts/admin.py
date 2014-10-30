from django.contrib import admin
from apps.accounts.models import *

admin.site.register(User)
admin.site.register(Role)
admin.site.register(MoveRoleRecord)
admin.site.register(LoginRecord)
admin.site.register(Organization)
admin.site.register(OrganizationMembership)
admin.site.register(OrganizationSettings)
admin.site.register(OrganizationStatistic)
admin.site.register(UserStatistic)