from django.conf import settings

from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import routers

from apps.accounts import views as account_views
from apps.contact import views as contact_views
from apps.documents import views as document_views
from apps.questions import views as question_views
from apps.processes import views as process_views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'contacts', contact_views.ContactFormViewSet)

router.register(r'accounts/organization', account_views.OrganizationViewSet)
router.register(r'accounts/register', account_views.RegisterViewSet)
router.register(r'accounts/user', account_views.UserViewSet)

router.register(r'accounts/login', account_views.LoginViewSet,
                base_name='login')

router.register(r'accounts/validate', account_views.ValidateUserViewSet,
                base_name='validate')

router.register(r'accounts/forgot_password',
                account_views.PasswordForgotViewSet,
                base_name='forgot_password')

router.register(r'accounts/reset_password',
                account_views.PasswordResetViewSet,
                base_name='reset_password')
router.register(r'processes/process_type',
                process_views.ProcessTypeViewSet,
                base_name='process_types')

router.register(r'documents/document', document_views.DocumentViewSet)
router.register(r'documents/live_document', document_views.LiveDocumentViewSet)

router.register(r'questions/question', question_views.QuestionViewSet)
router.register(r'processes/process', process_views.ProcessViewSet)
router.register(r'processes/process_instance',
                process_views.ProcessInstanceViewSet)

organization_router = routers.DefaultRouter()
organization_router.register(r'roles', account_views.RoleViewSet)
organization_router.register(r'memberships', account_views.MembershipViewSet)
organization_router.register(r'user', account_views.UserViewSet)

question_router = routers.DefaultRouter()
question_router.register(r'answers', question_views.AnswerViewSet)

process_router = routers.DefaultRouter()
process_router.register(r'steps', process_views.ProcessStepViewSet)
process_router.register(r'steps/(?P<step>\d+)/tasks',
                        process_views.ProcessStepTaskViewSet)

process_instance_router = routers.DefaultRouter()
process_instance_router.register(r'assignments',
                                 process_views.ProcessStepAssignmentViewSet)

live_document_router = routers.DefaultRouter()
live_document_router.register(r'sections',
                              document_views.LiveDocumentSectionViewSet)

api_urlpatterns = router.urls + \
    patterns('',
             url(r'^questions/question/(?P<question>\d+)/',
                 include(question_router.urls)),
             url(r'^processes/process/(?P<process>\d+)/',
                 include(process_router.urls)),
             url(r'^processes/process_instance/(?P<instance>\d+)/',
                 include(process_instance_router.urls)),
             url(r'^documents/live_document/(?P<live_document>\d+)/',
                 include(live_document_router.urls)),
             url(r'^accounts/organization/(?P<organization>\d+)/',
                 include(organization_router.urls)),
             url(r'^auth/', include('rest_framework.urls',
                                    namespace='rest_framework')))

app_view = TemplateView.as_view(template_name='app.html')
urlpatterns = patterns('',
                       url(r'^$', ensure_csrf_cookie(app_view), name='app'),
                       url(r'^api/', include(api_urlpatterns)),
                       url(r'^', include('apps.accounts.urls')),
                       url(r'^visual-admin/', include(admin.site.urls)))

#try:
#    exec('from visualorg.conf.environments.{}.urls import *'
#         .format(APP_ENVIRONMENT))
#except ImportError:
#    pass