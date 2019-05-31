"""AitomicGlobal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView
from django.conf.urls import *
from aitomic import views as aitomic_views
from django.conf import settings
from django.conf.urls.static import static
#from .task import prueba

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', include('aitomic.urls')),
	path('accounts/', include('django.contrib.auth.urls')),
	path('', TemplateView.as_view(template_name='home.html'), name='home'),
	url(r'signup/$', aitomic_views.signup, name='signup'),
	url(r'^account_activation_sent/$', aitomic_views.account_activation_sent, name='account_activation_sent'),
	url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
		aitomic_views.activate, name='activate'),
	url(r'^auth/', include('social_django.urls', namespace='social')),
	path('profile/<int:user_id>/', aitomic_views.user_profile, name='profile'),
	path('profile/<int:user_id>/photo', aitomic_views.user_profile_photo, name='profile'),
	path('myaccount/', aitomic_views.user_account, name='account'),
	path('myaccount/edit/', aitomic_views.edit_profile, name='edit_profile'),
	path('myaccount/password/', aitomic_views.change_password, name='change_password'),
	path('model/<int:model_id>/api/', aitomic_views.model_api, name='api'),
	path('model/<int:model_id>/restapi/', aitomic_views.rest_api, name='restapi'),
	path('model/<int:model_id>/results/', aitomic_views.model_results, name='results'),
	path('models/<int:user_id>/', aitomic_views.user_models, name='user_models'),
	path('payment_detail/<int:model_id>/', aitomic_views.payment_detail, name='payment_detail'),
	url('404', aitomic_views.error_404, name='error_404'),
	url('profile_error', aitomic_views.profile_error, name='profile_error'),
	url('500', aitomic_views.error_500,name='error_500'),
	path('about/', aitomic_views.landing, name='about'),
	path('model/<int:model_id>/comment/', aitomic_views.writeComment, name='comment'),
	path('model/<int:model_id>/list_comments/', aitomic_views.list_comments, name="list_comments"),
	path('download_data/', aitomic_views.user_data_download, name='download_data'),
	path('delete_account/', aitomic_views.remove_account2, name='remove_account'),
	url(r'^sw.js', (TemplateView.as_view(template_name="sw.js", content_type='application/javascript', )), name='sw.js'),
	url(r'^robots.txt', (TemplateView.as_view(template_name="robots.txt", content_type='text/plain', )), name='robots.txt')
]

handler404=aitomic_views.error_404
handler500=aitomic_views.error_500


if settings.DEBUG:
	urlpatterns += static(settings.MODEL_CONF_URL, document_root=settings.MODEL_CONF_ROOT)

#Do not delete this import, it creates the automatic tasks in automatic_tasks.py
import AitomicGlobal.automatic_tasks
