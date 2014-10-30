from apps.documents.models import *
from django.contrib import admin

admin.site.register(LiveDocument)
admin.site.register(LiveDocumentSection)
admin.site.register(LiveDocumentCompleteRecord)
admin.site.register(Document)
admin.site.register(DocumentVersion)
admin.site.register(DocumentComment)