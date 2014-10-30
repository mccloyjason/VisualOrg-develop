from django.contrib import admin
from apps.questions.models import *

admin.site.register(Question)
admin.site.register(Answer)