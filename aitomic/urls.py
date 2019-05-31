from django.contrib import admin
from django.urls import path, include
from .views import *
from django.conf.urls import url

urlpatterns = [
	# path('mail/', send_mail, name='mail'),
	path('uploadModel/', upload_model, name="uploadModel"),
	path('editModel/<int:model_id>/', edit_model, name="editModel"),
	path('model/<int:pk>/', ModelDetailView.as_view(), name='model_detail'),
	path('modelSearch/', model_search, name='model_search'),
	path('model/<int:model_id>/api/', model_api, name='api'),
	path('api/<int:model_id>/', rest_api, name='restapi'),
	path('fileOp/<int:model_id>/', fileOp, name='fileOp'),
	path('model/<int:model_id>/results/', model_results, name='results'),
	url(r'^i18n/', include('django.conf.urls.i18n')),
	path('landing/', landing, name='landing'),
	path('faq/', faq, name='faq'),
	path('userGuide/', user_guide, name='user_guide'),
	url(r'^model/buy/(?P<pk>\d+)/', payment_new, name='payment_model'),
	path('admin/userlist/', admin_user_list, name="admin_user_list"),
	path('admin/alert/', alert_users, name="admin_alert_users"),
	path('admin/banuser/<int:userid>/', admin_ban_user, name="admin_ban_user"),
	path('admin/unbanuser/<int:userid>/', admin_unban_user, name="admin_unban_user"),
	url(r'^model/score/(?P<pk>\d+)/', score_models, name='score_model'),
	path('changeLog/', change_log, name="changeLog"),
	path('deleteRevision/<int:revisionID>', delete_revision, name="deleteRevision"),
	path('newRevision/', new_revision, name="revisionDetails"),
	#path('payment/<int:model_id>/<int:quantity>/',paypal_payment, name='paypal_payment'),
	path('payment/approved/',paypal_payment_approved, name='paypal_payment_approved'),
	#path('legalTerms/', legal_terms, name="legalTerms"),
	path('guide/', guide, name="guide"),
	path('earn/',earn_benefits,name="earn_benefits"),
	path('codeEditor/<int:model_id>/',code_editor,name="code_editor")
]
