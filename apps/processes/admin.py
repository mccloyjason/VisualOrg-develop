from django.contrib import admin
from apps.processes.models import*

admin.site.register(Process)
admin.site.register(ProcessInstance)
admin.site.register(ProcessStep)
admin.site.register(ProcessStepAssignment)
admin.site.register(ProcessType)
admin.site.register(ProcessStepTask)