from django.contrib.auth import login
from .forms import *
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from AitomicGlobal.settings import AUTHENTICATION_BACKENDS as AUTH_BACKENDS, PERCENTAGE_FOR_PROVIDER
from django.db.models import Q, Func
from .views_utils import *
from django.views.generic.detail import DetailView
import base64
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from aitomic.forms import UserProfileForm, ProfileProfileForm
from django.http import HttpResponseNotFound, HttpResponseServerError, HttpResponse, HttpResponseRedirect
import logging
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import requests
import json
from .models import *
from aitomic.paypal import transaction, payouts
from ast import literal_eval
from django.http import JsonResponse
import csv
from django.contrib import messages
import datetime
import hashlib
from .views_utils import add_months


# Create your views here.
AITOMIC_MODEL_URL = '/model/'
API = 'api'
NOREPLY_AITOMIC_NET = 'noreply@aitomic.net'
ACTIVATE_ACCOUNT_SUBJECT = 'Activate your Aitomic account!'
PRICE_HAS_CHANGED_SUBJECT = 'One of your models\' price has changed'
LOW_CALLS = 'You are running out of calls!'
ZERO_CALLS = 'You have ran out of calls!'
SECURITY_ISSUE = _('Information about security issue')


def landing(request):
	return render(request, 'landing.html')


def faq(request):
	return render(request, 'faq.html')


def user_guide(request):
	return render(request, 'user_guide.html')


# def send_mail(request):
# 	sm('Subject test', 'Body test', 'noreply@aitomic.net', ['juanmiblancof@gmail.com'])
#
# 	return render(request, 'home.html')


def signup(request):
	if not request.user.is_anonymous:
		return redirect('/')
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():

			if len(request.FILES) > 0:
				encoded_photo = force_text(base64.b64encode(request.FILES["photo"].file.read()))
			else: 
				encoded_photo = json.load(open(os.path.join(os.getcwd(), 'aitomic/static/img/default_img.json')))["data"]

			user = form.save()
			# We set user fields
			set_fields(form, user, False, encoded_photo)  # We set is_active to false for verification email
			send_confirmation_mail(request, user)
			return redirect('account_activation_sent')

	else:
		form = SignUpForm()
	return render(request, 'signup.html', {'form': form})


def send_confirmation_mail(request, user):
	current_site = get_current_site(request)
	subject = ACTIVATE_ACCOUNT_SUBJECT
	message = render_to_string('account_activation_email.html', {
		'user': user,
		'domain': current_site.domain,
		'uid': force_text(urlsafe_base64_encode(force_bytes(user.pk))),
		'token': account_activation_token.make_token(user),
	})
	user.email_user(subject, message, from_email=NOREPLY_AITOMIC_NET)


def activate(request, uidb64, token):
	try:
		uid = force_text(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None

	if user is not None and account_activation_token.check_token(user, token):
		user.is_active = True
		user.profile.email_confirmed = True
		user.save()
		# We set django auth backend due to Google auth conflicts
		login(request, user, backend=AUTH_BACKENDS[-1])
		return redirect('home')
	else:
		return render(request, 'account_activation_invalid.html')


def account_activation_sent(request):
	return render(request, 'account_activation_sent.html')


def set_fields(form, user, active, encoded_photo):
	"""This method is used to set user fields"""

	user.refresh_from_db()
	user.first_name = form.cleaned_data.get('first_name')
	user.last_name = form.cleaned_data.get('last_name')
	user.email = form.cleaned_data.get('email')
	user.profile.birth_date = form.cleaned_data.get('birth_date')
	user.profile.photo = encoded_photo
	user.profile.description = form.cleaned_data.get('description')

	user.is_active = active
	user.save()


@login_required()
def upload_model(request):
	message = None
	error = ""
	try:
		if request.method == 'POST':

			form = AIModelForm(request.POST, request.FILES)
			if form.is_valid():
				check_required_files(request)

				input_example = check_file(request, "input_example")
				output_example = check_file(request, "output_example")
				ai_model_structure = None

				if "model" not in request.FILES.keys():
					ai_model_structure = request.FILES["ai_model_structure"].file.read()

				requirements = check_file(request, "requirements", optional=True)
				preprocess_code = check_file(request, "preprocess_code")
				postprocess_code = check_file(request, "postprocess_code")
				image_encoded = base64.b64encode(request.FILES["image"].file.read())

				ai_model = form.save(request.user, image_encoded, input_example, output_example,
									 ai_model_structure, requirements, preprocess_code, postprocess_code)

				ai_model.api_url = API + "/" + str(ai_model.id)  # FIXME: We should not save url when it's easy to auto generate
				ai_model.save()									 # FIXME: This line must disappear when url is deleted from databse
				if not isinstance(request.POST["measure"], list):
					measures = [request.POST["measure"]]
					values = [request.POST["value"]]
				else:
					measures = request.POST["measure"]
					values = request.POST["value"]

				for i in range(len(measures)):
					Measure.objects.create(type=measures[i], value=values[i], ai_model=ai_model)
				if not settings.DEBUG:
					if "model" not in request.FILES.keys():
						upload_to_server(request, "weights", ai_model.id, "weights.h5")
					elif request.POST["library"] == "Keras":
						upload_to_server(request, "model", ai_model.id, "model.h5")
					else:
						upload_to_server(request, "model", ai_model.id, "model.sav")

					if 'auxiliar_files' in request.FILES:
						upload_to_server(request, "auxiliar_files", ai_model.id, "auxiliar_files.zip")
					if 'ai_model_structure' in request.FILES.keys():
						deploy_api(ai_model, request.FILES['ai_model_structure'], preprocess_code, postprocess_code, request.POST["library"])
					else:
						deploy_api(ai_model, None, preprocess_code, postprocess_code,
								   request.POST["library"], request.FILES["model"])

				return redirect('home')
		else:
			form = AIModelForm()
	except ValidationError as err:
		logging.error("Validation error " + err.message)
		error = err.message

	return render(request, 'upload_model_form.html', {'form': form, 'message': message, "error": error})


def substractAPICall(user, model_id):
	print("Substracting call")
	model_bought = ModelBought.objects.filter(user=user, model_id=model_id)
	m_bought = None
	if model_bought.exists():
		for m in model_bought:
			if m.callable and m.callsLeft>0:
				m_bought = m
				break
	ai_model = AIModel.objects.filter(id=model_id)
	if ai_model.exists():
		calls = ApiCall.objects.filter(user=user, model=ai_model.first()).count()
	if (ai_model.exists() and ai_model.first().has_trial and settings.FREE_CALLS > calls):
		newcall = ApiCall.objects.create()
		newcall.user = user
		newcall.model = ai_model.first()
		newcall.is_free = True
		newcall.save()
	else:
		if model_bought.exists() and m_bought is not None and m_bought.callsLeft > 0:
			m_bought.callsLeft = m_bought.callsLeft -1
			m_bought.save()
			newcall = ApiCall.objects.create()
			newcall.user = user
			newcall.model = ai_model.first()
			newcall.is_free = False
			newcall.save()
			send_calls_reminder(ai_model.first(), m_bought, user, m_bought.totalCalls)


def send_calls_reminder(ai_model, m_bought, user, total_calls):
	if m_bought.callsLeft == round(total_calls * 0.1):
		subject = LOW_CALLS
		message = render_to_string('low_calls.html', {
			'user': user,
			'calls_left': m_bought.callsLeft,
			'model_name': ai_model.name,
		})
		user.email_user(subject, message, from_email=NOREPLY_AITOMIC_NET)
	elif m_bought.callsLeft == 0:
		subject = ZERO_CALLS
		message = render_to_string('zero_calls.html', {
			'user': user,
			'model_name': ai_model.name,
		})
		user.email_user(subject, message, from_email=NOREPLY_AITOMIC_NET)


@login_required()
def model_api(request, model_id):
	model_bought = ModelBought.objects.filter(user=request.user, model_id=model_id)
	m_bought = None

	if model_bought.exists():
		for m in model_bought:
			if m.callable and m.callsLeft>0:
				m_bought = m
				break
	ai_model = AIModel.objects.filter(id=model_id)
	free_calls = 0
	has_free_calls = False
	calls_left = 0
	total_calls = 0
	total_used_view = 0
	if ai_model.exists() and ai_model.first().has_trial:
		free_calls = ApiCall.objects.filter(user=request.user, model=ai_model.first(), is_free=True).count()
		has_free_calls = True

	if (model_bought.exists() and m_bought is not None and m_bought.callsLeft > 0) \
			or (ai_model.exists() and ai_model.first().has_trial and free_calls < settings.FREE_CALLS) \
			or (ai_model.exists() and ai_model.first().provider == request.user and not ai_model.first().final_mode and free_calls < settings.FREE_CALLS):
		if model_bought.exists():
			totalused = (m_bought.totalCalls - m_bought.callsLeft)
			send_calls_reminder(ai_model.first(), m_bought, request.user, m_bought.totalCalls - 1)
		try:
			model = AIModel.objects.get(id=model_id)		
			if request.method == 'POST':
				form = ApiModel(request.POST, request.FILES)
				if form.is_valid() and (request.FILES.get('photo', False) or request.FILES.get('input_text', False) or request.POST.get("manual_text", False)):
	
					headers = {'content-type': 'application/json', 'token': getToken(request.user.id)}
					dataSent = {}
					if request.FILES.get('photo', False):
						content = request.FILES["photo"]
						dataSent = {"data": base64.b64encode(content.read()).decode("utf-8")}

					elif request.FILES.get('input_text', False):
						input_file = request.FILES["input_text"].open(mode='rb')
						result_text = force_text(input_file.read())
						result_text = result_text.replace('\n', '')
						dataSent = {"data": result_text}
					else:
						manual_text = request.POST["manual_text"]
						dataSent = {"data": manual_text}
					#Parsing data introduced to object types
					if model.input_type == "Array of numbers":
						dataSent["data"] = [int(s) for s in dataSent["data"].split(',')]
					result = requests.post(url="http://localhost:80/api/"+ str(model_id) +"/", json=dataSent, headers=headers)
					# return redirect('model_results', model_id, result)
					return model_results(request, model_id, result, dataSent["data"])
				else:
					form = ApiModel()
					if m_bought is None:
						return render(request, 'models/model_api.html',
									  {'model': model, 'form': form, 'callsleft': settings.FREE_CALLS - free_calls,
									   'totalcalls': settings.FREE_CALLS, 'totalused': free_calls,
									   'free_calls': settings.FREE_CALLS - free_calls,
									   'has_free_calls': has_free_calls,
									   'callable': False})
					else:
						if has_free_calls:
							calls_left = m_bought.callsLeft + (settings.FREE_CALLS - free_calls)
							total_calls = m_bought.totalCalls + settings.FREE_CALLS
							total_used_view = totalused + free_calls
						else:
							calls_left = m_bought.callsLeft
							total_calls = m_bought.totalCalls
							total_used_view = totalused
						return render(request, 'models/model_api.html',
									  {'model': model, 'form': form,
									   'callsleft': calls_left,
									   'totalcalls':total_calls,
									   'totalused': total_used_view,
									   'free_calls': settings.FREE_CALLS - free_calls,
									   'has_free_calls': has_free_calls,
									   'callable': m_bought.callable})
			else:
				form = ApiModel()
				if m_bought is None: #test for free
					print(m_bought)
					return render(request, 'models/model_api.html',
								  {'model': model, 'form': form, 'callsleft': settings.FREE_CALLS - free_calls,
								   'totalcalls': settings.FREE_CALLS, 'totalused': free_calls,
								   'free_calls': settings.FREE_CALLS - free_calls,
									   'has_free_calls': has_free_calls,
									   'callable': False})
				else:
					if has_free_calls:
						calls_left = m_bought.callsLeft + (settings.FREE_CALLS - free_calls)
						total_calls = m_bought.totalCalls + settings.FREE_CALLS
						total_used_view = totalused + free_calls
					else:
						calls_left = m_bought.callsLeft
						total_calls = m_bought.totalCalls
						total_used_view = totalused
					print(calls_left)
					return render(request, 'models/model_api.html',
								  {'model': model, 'form': form,
								   'callsleft': calls_left,
								   'totalcalls': total_calls,
								   'totalused': total_used_view,
								   'free_calls': settings.FREE_CALLS - free_calls,
									'has_free_calls': has_free_calls,
									'callable': False})
		except Exception as e:
			logging.error(e)
			return redirect('/404')
	else:
		return redirect('/model/' + str(model_id) + "/")


@csrf_exempt
def rest_api(request, model_id):
	model = AIModel.objects.get(id=model_id)

	if request.method == 'POST':
		headers = {'content-type': 'application/json'}
		finalToken = None
		tokenHeader = "HTTP_TOKEN"
		for hd, val in request.META.items():
			if hd.startswith("HTTP_"):
				if hd.lower() == tokenHeader.lower():
					finalToken = val
				else:
					headers[hd.replace("HTTP_", "", 1)] = val

		if finalToken is not None:
			user = verifyTokenAndGetUser(finalToken)

			if user is not None:
				if model.provider.id != user.id:
					try:
						assert model.final_mode
					except:
						return HttpResponse("Error - API Call", content_type='application/json')
				moment_now = datetime.date.today()
				moment_now_1m = add_months(moment_now, -1)
				model_bought = ModelBought.objects.filter(user=user, model_id=model_id, moment_to_use__lte=moment_now).order_by("moment_to_use")
				m_bought = None
				if model_bought.exists():
					for m in model_bought:
						if m.callable and m.callsLeft>0:
							m_bought = m
							break
				ai_model = AIModel.objects.filter(id=model_id)
				free_calls = 0
				if ai_model.exists() and ai_model.first().has_trial:
					free_calls = ApiCall.objects.filter(user=user, model=ai_model.first(), is_free=True).count()
				if (model_bought.exists() and m_bought is not None and m_bought.callsLeft > 0 and not m_bought.has_expired) \
						or (ai_model.exists() and ai_model.first().has_trial and free_calls < settings.FREE_CALLS) \
						or (
						ai_model.first().provider == user and not ai_model.first().final_mode):
					
					jsonBody = json.loads(request.body)
					until = ""
					if 'until' in jsonBody:
						until = jsonBody["until"]
					jsonContent = {"data": jsonBody["data"], "type": model.input_type, "until": until}
					substractAPICall(user, model_id)
					response = requests.post(url="http://" + "ai-" + str(model_id) + ":8600/main", json=jsonContent,
											 headers=headers)
					return HttpResponse(response, content_type='application/json')
				else:
					return HttpResponse("0 calls left", content_type='application/json')
			else:
				return HttpResponse("Unauthenticated", content_type='application/json')
		else:
			return HttpResponse("No token", content_type='application/json')
	return redirect("/404")


	
@csrf_exempt
def fileOp(request, model_id):
	model = AIModel.objects.get(id=model_id)
	if request.method == 'POST':
		headers = {'content-type': 'application/json'}
		finalToken = None
		tokenHeader = "HTTP_TOKEN"

		for hd, val in request.META.items():
			if hd.startswith("HTTP_"):
				if hd.lower() == tokenHeader.lower():
					finalToken = val


		if finalToken is not None:
			user = verifyTokenAndGetUser(finalToken)

			if user is not None:
				if model.provider.id == user.id:
					try:
						assert not model.final_mode
					except:
						return HttpResponse("Error - API Call", content_type='application/json')

					ai_model = AIModel.objects.filter(id=model_id)
					jsonBody = json.loads(request.body)
					jsonContent = {"file": jsonBody["file"], "type": jsonBody["type"], "content": jsonBody["content"]}
					response = requests.post(url="http://" + "ai-" + str(model_id) + ":8600/" + jsonBody["op"], json=jsonContent,
											 headers=headers)
					return HttpResponse(response, content_type='application/json')
				return HttpResponse("Unauthenticated", content_type='application/json')
		else:
			return HttpResponse("No token", content_type='application/json')
	return redirect("/404")

@login_required()
def model_results(request, model_id, result, dataSent):
	model = AIModel.objects.get(id=model_id)
	return render(request, 'models/model_results.html', {'model': model, 'input': dataSent, 'result': result.content.decode("utf8")})


def model_search(request):
	models_search = []
	user = request.user
	if request.method == "GET":
		form = SearchModelForm()
		request_type = request.GET
	else:
		form = SearchModelForm(request.POST)
		request_type = request.POST

	order, querys = search_conditions(request_type)

	if querys:
		if order:
			models_search = AIModel.objects.filter(querys, deletion_date__isnull=True).exclude(final_mode=False).order_by(order)
		else:
			models_search = AIModel.objects.filter(querys, deletion_date__isnull=True).exclude(final_mode=False)
	else:
		if order:
			models_search = AIModel.objects.filter(deletion_date__isnull=True).exclude(final_mode=False).order_by(order)
		else:
			models_search = AIModel.objects.filter(deletion_date__isnull=True).exclude(final_mode=False)

	if request.method == "GET":
		return render(request, 'model_search.html', {'models_search': models_search, 'form': form, 'user': user})
	else:
		return render(request, 'ajax/model_search.html', {'models_search': models_search, 'form': form, 'user': user})


def search_conditions(request_type):
	models_search = []
	querys = []
	q = ""
	rating = ""
	order_by = ""

	if 'select_order' in request_type:
		order = request_type.get('select_order')
		if order:
			switcher = {
				"1": "price_hundred_calls",
				"2": "-price_hundred_calls",
				"3": "rating",
				"4": "-rating",
				"5": "name",
				"6": "provider",
			}
			order_by = switcher[order]
	if 'p_search' in request_type:
		q = request_type.get('p_search')
		if q:
			querys = (Q(name__icontains=q) | Q(general_description__icontains=q) | Q(tags__icontains=q))
			user = User.objects.filter(username__icontains=q)
			if user:
				user_id = user[0].id
				if querys:
					querys |= (Q(provider=user_id))
				else:
					querys = (Q(provider=user_id))
	if 'rating' in request_type:
		rating = request_type.get('rating')
		if rating:
			if querys:
				querys &= (Q(rating__gte=rating))
			else:
				querys = (Q(rating__gte=rating))
	if 'min_price' or 'max_price' in request_type:
		min_price = request_type.get('min_price')
		max_price = request_type.get('max_price')
		if min_price == '' and max_price:
			min_price = 0
		if max_price == '' and min_price:
			max_price = 1000000
		if (min_price or min_price == 0) and max_price:
			if querys:
				querys &= (Q(price_hundred_calls__gte=min_price) & Q(price_hundred_calls__lte=max_price))
			else:
				querys = (Q(price_hundred_calls__gte=min_price) & Q(price_hundred_calls__lte=max_price))
	if querys:
		models_search = AIModel.objects.filter(querys)
		querys &= (Q(final_mode=True))
	else:
		models_search = AIModel.objects.all()
		querys = Q(final_mode=True)

	return order_by, querys


def error_404(request):
	render_view = render(request, 'error.html', {'error': '404'})
	return HttpResponseNotFound(render_view)

def profile_error(request):
	render_view = render(request, 'profile_error.html')
	return HttpResponseNotFound(render_view)

def error_500(request):
	render_view = render(request, 'error.html', {'error': '500'})
	return HttpResponseServerError(render_view)


def user_profile(request, user_id):

	try:
		profile = Profile.objects.get(pk=user_id)

		if profile.deletion_date != None:
			return redirect('/404')
		else:
			my_models = []
			num_models = 0
			user_models = AIModel.objects.filter(provider=profile.user.id)
			num_models = len(user_models)
			same_user = True if request.user.id == user_id else False

			return render(request, 'profile/user_profile.html',
						{'profile': profile, 'num_models': num_models, 'same_user': same_user})
	except Exception as e:
		return redirect('/profile_error')


def user_profile_photo(request, user_id):
	profile = Profile.objects.get(pk=user_id)
	image = base64.b64decode(profile.photo)
	return HttpResponse(image, content_type="image/jpeg")


@login_required()
def user_account(request):
	profile = Profile.objects.get(user=request.user)

	# User statistics
	num_models_sold = 0
	models_sold = 0
	money_made = 0
	num_models_bought = 0
	money_spent = 0
	list_models = []
	list_payments = []
	list_buyers = []
	num_models_acc = 0
	num_buyers = 0

	# a) num models i have sold:
	total_my_models = AIModel.objects.filter(provider_id = request.user.id)

	for models in total_my_models:

		list_models.append(models)
		if Payment.objects.filter(model = models):
			models_sold += 1
			act_payment = Payment.objects.filter(model = models)
			num_buyers = len(act_payment)
			list_buyers.append(num_buyers)

			for payments in act_payment:
				num_models_sold += payments.quantity
				num_models_acc += payments.quantity


				# b) money i have made:
				money_made += payments.price

			# c) num people who bought every model:
			list_payments.append(num_models_acc)
			num_models_acc = 0

	num_clients_by_model = zip(list_models, list_payments, list_buyers)

	# d) models i have bought:
	models_bought = ModelBought.objects.filter(user_id = request.user.id)
	modelsx = ModelBought.objects.filter(user_id = request.user.id)
	
	models_distinct = []
	for models in models_bought:
		act_model = AIModel.objects.get(id = models.model_id)
		if models not in models_distinct:
			models_distinct.append(models)

		num_models_bought = len(models_distinct)

		# e) money i have spent:
		money_spent += round((act_model.price_hundred_calls/100) * models.totalCalls, 2)

	user_id = request.user.id
	user_models = AIModel.objects.filter(provider=user_id)

	num_models = len(user_models)
	return render(request, 'profile/my_account.html', {'profile': profile, 'num_models': num_models, 'num_models_bought': num_models_bought, 'money_spent': money_spent, 'num_models_sold': num_models_sold, 'money_made': money_made, 'num_clients_by_model': num_clients_by_model, 'models_sold': models_sold})


@login_required()
def edit_profile(request):
	user = User.objects.get(pk=request.user.pk)
	profile = user.profile

	if request.method == 'POST':
		user_form = UserProfileForm(request.POST, instance=user)
		profile_form = ProfileProfileForm(request.POST, request.FILES, instance=profile)

		if user_form.is_valid() and profile_form.is_valid():

			if len(request.FILES) > 0:
				encoded_photo = force_text(base64.b64encode(request.FILES["photo"].file.read()))
			else:
				encoded_photo = user.profile.photo

			profile_form.save(user, encoded_photo)
			user_form.save(user)

			return redirect('/myaccount/')

	else:
		user_form = UserProfileForm(instance=user)
		profile_form = ProfileProfileForm(instance=profile)

	context = {
		'user_form': user_form,
		'profile_form': profile_form,
		'user': user
	}

	return render(request, 'profile/edit_account.html', context)


@login_required()
def change_password(request):
	if request.method == "POST":
		change_password_form = PasswordChangeForm(request.user, request.POST)
		if change_password_form.is_valid():
			user = change_password_form.save()
			update_session_auth_hash(request, user)

			return redirect("/myaccount/")

		else:
			args = {'change_password_form': change_password_form}
			return render(request, 'profile/change_password.html', args)
	else:
		change_password_form = PasswordChangeForm(request.user)

		args = {'change_password_form':change_password_form}

		return render(request,'profile/change_password.html',args)


class ModelDetailView(DetailView):
	model = AIModel
	context_object_name = 'aimodel'
	template_name = 'model_detail.html'

	def get_context_data(self, **kwargs):
		context = super(ModelDetailView, self).get_context_data(**kwargs)
		context['user'] = self.request.user
		context['tags'] = self.get_object().tags.split(',')
		context['model_bought'] = False
		context['user_can_rate'] = False
		context['user_rating'] = 0
		context['draft_and_not_creator'] = False

		model = AIModel.objects.get(pk=self.get_object().id)
		if not model.final_mode and model.provider != self.request.user:
			context['draft_and_not_creator'] = True

		if self.request.user.is_authenticated:
			mbs = ModelBought.objects.filter(user=self.request.user)

			model_bought = ModelBought.objects.filter(user_id=self.request.user.id,
																 model_id=self.get_object().id,
			                                                     moment_to_use__lte=datetime.datetime.now().date()
			                                                    #  moment_to_use__gte=add_months(datetime.datetime.now().date(),-1)
			                                                     )
			context['model_bought'] = False
			context['callsleft'] = 0
			m_bought = None
			if model_bought.exists():
				for m in model_bought:
					if m.callable and m.callsLeft>0:
						context['model_bought'] = True
						context['callsleft'] = m.callsLeft
						break
			else: 
				context['callsleft'] = 0
			context['has_trials'] = ApiCall.objects.filter(user=self.request.user, model=self.get_object(), is_free=True).count() < 10
			vote = Vote.objects.filter(user_id=self.request.user.id, model_id=self.get_object().id)

			if vote:
				context['user_rating'] = str(vote.first().value)

			for mb in mbs:
				if mb.model.id == model.id:
					context['user_can_rate'] = True

		context['comments'] = Comment.objects.filter(model=self.get_object())

		context['free_trial'] = self.get_object().has_trial
		context['is_creator'] = self.request.user.id == self.get_object().provider.id

		return context


@login_required()
def payment_new(request, pk):
	model = AIModel.objects.get(pk=pk)
	try:
		assert model.final_mode and model.deletion_date is None
	except:
		return redirect("/500")

	if request.method == "POST":
		form = PaymentForm(request.POST)
		if form.is_valid():
			quantity = form.cleaned_data.get('quantity')
			moment_to_use = form.cleaned_data.get('moment_to_use')
			if moment_to_use is None:
				moment_to_use = datetime.date.today()
			model_id = request.POST.get('model_id')

			return paypal_payment(request, model_id=model_id, quantity=quantity, moment_to_use=moment_to_use)

	else:
		form = PaymentForm()

	models_bought = ModelBought.objects.filter(user=request.user, model_id=pk, callsLeft__gt=0,
											   moment_to_use__gte=add_months(datetime.date.today(),-1))
	if models_bought.exists():  # Checks if the user has already bought the model and has calls left
		args = {'model': model, 'form': form, 'bought': True, 'models_bought': models_bought}

	else:
		args = {'model': model, 'form': form, 'bought': False}

	return render(request, 'payment_new.html', args)


@login_required()
def paypal_payment(request, model_id, quantity, moment_to_use):
	model = AIModel.objects.get(pk=model_id)
	try:
		assert model.final_mode
	except:
		return redirect("/500")
	price = round((int(quantity) / 100) * model.price_hundred_calls.__float__(), 2)
	moment_to_use_date = moment_to_use
	moment_to_use = moment_to_use.__str__()
	moment_to_use = moment_to_use.replace("-", "")

	args = {'model': model, 'quantity': quantity, 'price': price, 'moment_to_use': moment_to_use, 'moment_to_use_date':moment_to_use_date}

	return render(request, 'paypal_payment.html', args)


@login_required()
@csrf_exempt
def paypal_payment_approved(request):
	if request.method == "POST":
		json_body_string = request.body.decode('utf8')
		list_string = literal_eval(json_body_string)
		order_id = list_string['orderID']
		model_id = list_string['modelID']
		quantity = list_string['quantity']
		moment_to_use = list_string['moment_to_use']
		user = request.user

		try:
			model = AIModel.objects.get(pk=model_id)
			assert model.final_mode
			order = transaction.GetOrder().get_order(order_id=order_id, model_id=model_id, user=user, quantity=quantity, moment_to_use=moment_to_use)
		except Exception as e:
			return redirect('/500')

		return redirect('/model/' + str(model_id))
	else:
		return redirect('/404')


def user_models(request, user_id):
	if request.user.id is None:
		profile_id = 0
	else:
		profile_id = request.user.profile.id

	user_models = AIModel.objects.filter(provider=user_id)
	purchased_models = []
	my_models = False

	if request.user.id == user_id:
		models_bought = ModelBought.objects.filter(user_id=user_id)
		my_models = True
		user_models = AIModel.objects.filter(provider=user_id)

		for mb in models_bought:
			purchased_models.append(mb.model)
	
	else:
		user_models = AIModel.objects.filter(provider=user_id, final_mode=True)

	return render(request, 'models/user_models.html',
				  {'user_models': user_models, 'user_id': user_id, 'profile_id': profile_id, 'my_models': my_models,
				   'purchased_models': purchased_models})


# Methods for List User VIEW / Ban user VIEW
@login_required
def admin_user_list(request):
	if request.user.is_staff:
		userList = User.objects.all()
		return render(request, 'admin/userlist.html',
					  {'userList': userList})
	else:
		return error_404(request)


@login_required
def admin_ban_user(request, userid):
	if request.user.is_staff:
		bannedUser = User.objects.get(pk=userid)
		bannedUser.is_active = False
		bannedUser.save()
		return admin_user_list(request)
	else:
		return error_404(request)


@login_required
def admin_unban_user(request, userid):
	if request.user.is_staff:
		unbannedUser = User.objects.get(pk=userid)
		unbannedUser.is_active = True
		unbannedUser.save()
		return admin_user_list(request)
	else:
		return error_404(request)


def writeComment(request, model_id):
	model = AIModel.objects.get(id=model_id)
	model_bought = ModelBought.objects.filter(user=request.user, model_id=model_id)

	if request.method == 'POST':
		form = WriteCommentForm(request.POST)

		if form.is_valid():
			# TODO: Fix this please, badges always true
			comment = Comment(text=form.cleaned_data.get('text'), badge=model_bought.exists(), model=model,
							  user=request.user)
			comment.save()
			return HttpResponseRedirect('/model/' + str(model_id))
	else:
		form = WriteCommentForm()

	return render(request, 'models/write_comment.html', {'form': form, 'model_id': model_id})


def list_comments(request, model_id):
	model = AIModel.objects.get(id=model_id)
	num_page = 5
	pagination = int(request.GET['pagination'])
	init = (pagination - 1) * num_page
	end = pagination * num_page
	data = list(Comment.objects.filter(model=model).values().order_by('-date')[init:end])

	for i in data:
		try:
			user = Profile.objects.get(user_id=i['user_id'])
			i['username'] = user.user.username
		except Exception as e:
			i['username'] = 'Removed account'
	return JsonResponse(data, safe=False)


@login_required()
def edit_model(request, model_id):
	message = None
	error = ""
	image_encoded = None
	price_changed = False
	form_route = ""
	ai_model_to_deploy = None
	ai_model_structure = None
	possible_deletion_date = None
	can_be_eliminated = False

	try:
		model = AIModel.objects.get(pk=model_id)
		assert model.provider == request.user
		form_route = 'edit_model_form.html'
		possible_deletion_date = add_months(datetime.date.today(), 1)

		# Edit model when the model is final
		if model.final_mode:
			if request.method == 'POST':
				form = EditAIModelForm(request.POST, request.FILES)
				if form.is_valid():

					price_changed = form.cleaned_data['price_hundred_calls'] != model.price_hundred_calls

					if len(request.FILES) != 0:
						image_encoded = base64.b64encode(request.FILES["image"].file.read())

					measure = Measure.objects.get(ai_model=model)

					# If marked for deletion
					deletion_date = None
					if form.cleaned_data['delete']:
						if model.deletion_date is None:
							deletion_date = add_months(datetime.date.today(), 1)
						else:
							deletion_date = model.deletion_date

					form.save(model, measure, image_encoded, deletion_date)

					# We send an email whe price changes to warn users
					if price_changed:
						boughts = ModelBought.objects.filter(model=model)
						for mb in boughts:
							message = render_to_string('price_changed_email.html', {
								'user': mb.user,
								'model_name': model.name,
								'new_price': form.cleaned_data['price_hundred_calls'],
							})
							mb.user.email_user(PRICE_HAS_CHANGED_SUBJECT, message, from_email=NOREPLY_AITOMIC_NET)

					return redirect(AITOMIC_MODEL_URL + str(model_id) + '/')
			else:
				measure = Measure.objects.get(ai_model=model)
				deletion = False
				if model.deletion_date is not None:
					deletion = True
				args = {}
				form = EditAIModelForm(initial={'name': model.name,
												'general_description': model.general_description,
												'image': model.image,
												'technical_description': model.technical_description,
												'price_hundred_calls': model.price_hundred_calls,
												'tags': model.tags,
												'measure': measure.type,
												'value': measure.value,
												'delete': deletion})
		else:
			form_route = 'upload_model_form.html'
			# Edit model when the model is NOT final
			if request.method == 'POST':
				if request.POST.get('delete') is not None:  ## User clicked "delete model"
					model.delete()
					return redirect('/models/'+str(request.user.id))

				form = AIModelForm(request.POST, request.FILES)
				if form.is_valid():
					input_example = check_file(request, "input_example")  # if empty = ""
					output_example = check_file(request, "output_example")  # if empty = ""
					library = request.POST["library"]  # if empty = ""
					if 'ai_model_structure' in request.FILES:
						ai_model_structure = request.FILES["ai_model_structure"].file.read()
					requirements = check_file(request, "requirements", optional=True)  # if empty = ""
					preprocess_code = check_file(request, "preprocess_code")
					postprocess_code = check_file(request, "postprocess_code")
					if 'image' in request.FILES:
						image_encoded = base64.b64encode(request.FILES["image"].file.read())

					measure = Measure.objects.get(ai_model=model)

					ai_model = form.update(model, measure, image_encoded, input_example, output_example,
										   ai_model_structure,
										   requirements, preprocess_code, postprocess_code, library)

					if not settings.DEBUG:
						if "model" not in request.FILES.keys() and "weights" in request.FILES.keys():
							upload_to_server(request, "weights", ai_model.id, "weights.h5")
						elif request.POST["library"] == "Keras" and "model" in request.FILES.keys():
							upload_to_server(request, "model", ai_model.id, "model.h5")
						elif "model" in request.FILES.keys():
							upload_to_server(request, "model", ai_model.id, "model.sav")

						if 'auxiliar_files' in request.FILES:
							upload_to_server(request, "auxiliar_files", ai_model.id, "auxiliar_files.zip")
						if 'ai_model_structure' in request.FILES.keys() or ai_model.ai_model_structure != None or ai_model.ai_model_structure != "":
							if "ai_model_structure" in request.FILES.keys():
								deploy_api(ai_model, request.FILES['ai_model_structure'], preprocess_code, postprocess_code,
										   request.POST["library"])
							else:
								deploy_api(ai_model, ai_model.ai_model_structure, preprocess_code,
							   				postprocess_code,
										   request.POST["library"])
						else:
							if "model" in request.FILES.keys():
								deploy_api(ai_model, None, preprocess_code, postprocess_code,
										   request.POST["library"], request.FILES["model"])
							else:
								raise ValidationError("Must specify the entire model.")

					return redirect(AITOMIC_MODEL_URL + str(model_id) + '/')
			else:
				measure = Measure.objects.get(ai_model=model)
				form = AIModelForm(initial={'name': model.name,
											'general_description': model.general_description,
											# image
											'input_example_text': model.input_example,
											'input_type': model.input_type,
											'output_example_text': model.output_example,
											'output_type': model.output_type,
											# 'ai_model_structure': ai_model_structure,
											'requirements_text': model.requirements,
											'technical_description': model.technical_description,
											'preprocess_code_text': model.preprocess_code,
											'postprocess_code_text': model.postprocess_code,
											'price_hundred_calls': model.price_hundred_calls,
											'tags': model.tags,
											'measure': measure.type,
											'value': measure.value,
											'final_mode': model.final_mode,
											'has_trial': model.has_trial})
				can_be_eliminated = True

	except ValidationError as err:
		logging.error("Validation error" + err.message)
		error = err.message
	except AssertionError as err2:
		logging.error("Assertion error" + err2.message)
		return error_500(request)
	except AIModel.DoesNotExist:
		return error_404(request)

	return render(request, form_route,
				  {'form': form, 'message': message, "error": error, "possible_deletion_date": possible_deletion_date, 'can_be_eliminated': can_be_eliminated})


@login_required
def score_models(request, pk):
	value = request.POST.get('rating')
	model = AIModel.objects.get(pk=pk)
	user_vote = Vote.objects.filter(user_id=request.user.id, model_id=model.id)

	if request.method == "GET":
		model = AIModel.objects.get(pk=pk)
		form = VoteModelForm()

	else:
		form = VoteModelForm(request.POST)
		if form.is_valid():
			if user_vote:
				user_vote.update(value=value)
			else:
				vote = Vote.objects.create()
				vote.user = request.user
				vote.model = model
				vote.value = value
				vote.save()

			rating = rating_average(model)

			model.rating = rating
			model.save()

			return JsonResponse({'avg_rating': rating})


def rating_average(model):
	votes_list = list(Vote.objects.filter(model=model))
	sum = 0
	number_vot = 0
	for m in votes_list:
		if m.value:
			sum += m.value
			number_vot += 1

	rating = sum / number_vot
	return rating


def change_log(request):
	revisions = Revision.objects.order_by('-publication_date')
	if len(revisions) > 0:
		return render(request, 'change_log.html', {"revisions": revisions})
	else:
		return render(request, 'change_log.html')


@login_required()
def delete_revision(request, revisionID):
	if not request.user.is_staff:
		return redirect('/404')
	revision = Revision.objects.filter(pk=revisionID)[0]

	if revision is not None:
		revision.delete()
		return redirect('/changeLog/')

@login_required()
def new_revision(request):
	if not request.user.is_staff:
		return redirect('/404')
	if request.method == 'POST':
		revision_form = RevisionForm(request.POST)
		if revision_form.is_valid():
			revision = Revision.objects.create()
			revision.version = request.POST["version"]
			revision.photo = force_text(base64.b64encode(request.FILES["photo"].file.read()))
			revision.description = request.POST["description"]
			revision.description_es = request.POST["description_es"]
			revision.save()
			return redirect('/changeLog/')
	else:
		revision_form = RevisionForm()

	return render(request, 'revisionDetails.html', {'form': revision_form})


def guide(request):
	return render(request, 'guide.html')


def getToken(idUser):
	user = User.objects.get(pk=idUser)
	uid = hashlib.sha256((str(idUser) + "|" + user.username + "|" + "aitomicMolaSlackbotNo" + "|" + str(user.date_joined)).encode('utf-8')).hexdigest()
	finalToken = base64.b64encode(bytes(str(idUser) + "|" + uid, 'utf-8'))
	#fixme: delete print?
	return force_text(finalToken)


def verifyTokenAndGetUser(token):
	try:
		tokenString = base64.b64decode(token).decode('utf-8')
		userID = tokenString.split("|")[0]
		if userID != None:
			realToken = getToken(userID)
			print("Comparing " + realToken + " - " + token) 
			if realToken == token:
				return User.objects.get(pk=userID)
	except:
		return None
	return None


@login_required
def user_data_download(request):
	profile_data = Profile.objects.all().filter(user_id=request.user.id)

	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="user_data.csv"'

	writer = csv.writer(response, delimiter=',')
	writer.writerow([',username', 'first_name', 'last_name', 'email', 'birth_date', 'description'])

	for data in profile_data:
		writer.writerow([data.user.username, data.user.first_name, data.user.last_name, data.user.email,
						 data.birth_date, data.description])

	return response


@login_required()
def remove_account2(request):
	deletion_date = None
	user = User.objects.get(id=request.user.id)
	user_models = AIModel.objects.filter(provider_id=user.id)

	if user.profile.deletion_date is None:
		deletion_date = add_months(datetime.date.today(), 1)
		for model in user_models:
			model.deletion_date = deletion_date
			model.save()

		user.profile.deletion_date = deletion_date
		user.save()
	else:
		deletion_date = user.profile.deletion_date

	return render(request, 'home.html')


@login_required()
def earn_benefits(request):
	user_id = request.user.id
	money_and_calls_to_reclaim = payouts.get_money_and_calls(user_id)
	total_money = money_and_calls_to_reclaim.get('total_money')
	total_calls_sold = money_and_calls_to_reclaim.get('total_calls_sold')

	if request.method == "POST":
		form = EarnBenefitsForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data.get('paypal_email_1')
			try:
				response = payouts.send_payout(total_money, email, user_id)
				if response.status_code == 201:
					payouts.set_payments_reclaimed(user_id)
					return render(request, 'profile/payout_success.html',{'email': email})
				else:
					return render(request, 'profile/payout_error.html')  # Paypal gateway error
			except Exception as e:
				print(e)
				return render(request, 'profile/payout_error.html')

	else:
		form = EarnBenefitsForm()


	args = {'form': form, 'total_money': total_money, 'total_calls_sold': total_calls_sold}
	return render(request, 'profile/earn_benefits.html', args)


@login_required()
def payment_detail(request, model_id):

	aimodel = AIModel.objects.get(pk=model_id)
	models_bought = ModelBought.objects.filter(user=request.user, model=aimodel)
	model_api_url = aimodel.api_url  # FIXME: We must generate URL here instead of getting it from DB
	api_token = getToken(request.user.id)
	calls_made = []
	expiration_calls = []

	if models_bought:
		for mb in models_bought:
			expiration_date = mb.ending_moment
			expiration_calls.append(expiration_date)
			calls_made.append(mb.totalCalls-mb.callsLeft)

	models_bought_calls_left = zip(models_bought, expiration_calls, calls_made)

	return render(request, 'payment_detail.html', {'model_api_url': model_api_url, 'models_bought_calls_left': models_bought_calls_left, 'api_token': api_token})


@login_required()
def code_editor(request, model_id):
	model = AIModel.objects.get(id=model_id)
	if model.final_mode or model.provider_id != request.user.id:
		return redirect('/404')
	return render(request, 'code_editor.html', {'modelid': model.id, 'token': getToken(request.user.id)})


@login_required
def alert_users(request):
	if request.user.is_staff:
		if request.method == "POST":
			form = AlertForm(request.POST)
			if form.is_valid():
				send_alert(form.cleaned_data['text'])

				form = AlertForm()
				return render(request, 'alert_form.html', {'form': form, 'correct_message': True})
		else:
			form = AlertForm()
			return render(request, 'alert_form.html', {'form': form, 'correct_message': False})
	else:
		return error_404(request)


def send_alert(text):
	users = User.objects.filter(is_staff=False, is_active=True)
	subject = SECURITY_ISSUE
	for user in users:
		message = render_to_string('alert_email.html', {
			'user': user,
			'text': text,
		})
		user.email_user(subject, message, from_email=NOREPLY_AITOMIC_NET)
