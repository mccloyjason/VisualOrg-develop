from django.conf.urls import url
from apps.accounts.views import Login,Home

urlpatterns = [
    url(r'^dashboard/$', Login.as_view(),name='login'),
    url(r'^home/$', Home.as_view(),name='home'),
    url(r'^logout/$', 'apps.accounts.views.logout',name='logout'),
]