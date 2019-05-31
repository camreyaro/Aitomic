from .models import *
from django.core.files.storage import FileSystemStorage
import subprocess
import os
import logging
from django.core.exceptions import ValidationError
import datetime
import calendar

STRUCTURE_NAME = "model"
REQUIREMENTS_NAME = "requirements.txt"
PREPROCESS_NAME = "preprocess.py"
POSTPROCESS_NAME = "postprocess.py"
AUXILIAR_FILES_NAME = "auxiliar_files.zip"
ROOT = "root"
OVH_IP = "54.38.65.178"


def upload_to_server(request, field_name, model_id, filename):
	"""
	This function uploads a file to the server
	:param request: request of the view method
	:param file_name: file name of the request.FILES
	:return: None
	"""
	file = request.FILES[field_name]
	fs = FileSystemStorage(location=settings.MODEL_CONF_ROOT + '/' + str(request.user.id) + '/' + str(model_id) + '/')

	fs.save(filename, file)

	server_password = os.environ.get('SERVER_PASSWORD')
	logging.debug("Creating directories...")
	subprocess.call(
		"sshpass -p " + server_password + " ssh -o StrictHostKeyChecking=no " + ROOT + "@" + OVH_IP + " mkdir -p " + settings.REMOTE_AITOMIC_FILES,
		shell=True)
	subprocess.call(
		"sshpass -p " + server_password + " ssh -o StrictHostKeyChecking=no " + ROOT + "@" + OVH_IP + " mkdir -p " + settings.REMOTE_AITOMIC_FILES + "/" + str(
			request.user.id), shell=True)
	subprocess.call(
		"sshpass -p " + server_password + " ssh -o StrictHostKeyChecking=no " + ROOT + "@" + OVH_IP + " mkdir -p " + settings.REMOTE_AITOMIC_FILES + "/" + str(
			request.user.id) + "/" + str(model_id), shell=True)
	logging.debug("Uploading files...")
	subprocess.call("sshpass -p " + server_password + " scp -r" + " " + settings.MODEL_CONF_ROOT + '/' +
					str(request.user.id) + '/' + str(
		model_id) + '/' + filename + " " + ROOT + "@" + OVH_IP + ":" + settings.REMOTE_AITOMIC_FILES + "/" +
					str(request.user.id) + '/' + str(model_id) + '/', shell=True)

	os.remove(settings.MODEL_CONF_ROOT + '/' + str(request.user.id) + '/' + str(model_id) + '/'+filename)


def load_file(file_content, user, model_id, filename):
	if not os.path.exists(settings.MODEL_CONF_ROOT):
		os.makedirs(settings.MODEL_CONF_ROOT)
	if not os.path.exists(settings.MODEL_CONF_ROOT + '/' + str(user.id)):
		os.makedirs(settings.MODEL_CONF_ROOT + '/' + str(user.id))
	if not os.path.exists(settings.MODEL_CONF_ROOT + '/' + str(user.id) + '/' + str(model_id)):
		os.makedirs(settings.MODEL_CONF_ROOT + '/' + str(user.id)+ '/' + str(model_id))
	if not os.path.exists(settings.MODEL_CONF_ROOT + '/' + str(user.id) + '/' + str(model_id)):
		os.makedirs(settings.MODEL_CONF_ROOT + '/' + str(user.id)+ '/' + str(model_id))

	with open(settings.MODEL_CONF_ROOT + '/' + str(user.id) + '/' + str(model_id) + '/' + filename, "w+") as f:
		f.write(file_content)

	server_password = os.environ.get('SERVER_PASSWORD')
	subprocess.call("sshpass -p " + server_password + " scp -r" + " " + settings.MODEL_CONF_ROOT + '/' +
					str(user.id) + '/' + str(
		model_id) + '/' + filename + " " + ROOT + "@" + OVH_IP + ":" + settings.REMOTE_AITOMIC_FILES +
					"/" + str(user.id) + '/' + str(model_id) + '/', shell=True)

	os.remove(settings.MODEL_CONF_ROOT + '/' + str(user.id) + '/' + str(model_id) + '/' + filename)


def check_file(request, input_name, optional=False):
	if input_name in request.FILES.keys():
		if input_name == 'preprocess_code' or input_name == 'postprocess_code':
			file = request.FILES[input_name].open(mode='rb')
			result = file.read()
		else:
			result = request.FILES[input_name].file.read()
	elif input_name in request.POST.keys() and len(request.POST[input_name + '_text']) > 0:
		result = request.POST[input_name + '_text']
	else:
		if not optional:
			raise ValidationError("You must specify " + input_name)
		else:
			result = ""

	return result


def check_required_files(request):
	if 'image' not in request.FILES:
		raise ValidationError("Image is compulsory")
	if 'ai_model_structure' not in request.FILES and 'model' not in request.FILES:
		raise ValidationError("You must specify a model")
	elif 'weights' not in request.FILES and 'model' not in request.FILES:
		raise ValidationError("Weights file is compulsory")


def deploy_api(ai_model, ai_model_structure, preprocess_code, postprocess_code, library, model=None):
	model_id = ai_model.id
	provider = ai_model.provider
	print("Extra files...")

	if ai_model_structure is not None:
		if isinstance(ai_model_structure, str):
			if ai_model_structure.strip().startswith("{"):
				extension = ".json"
			else:
				extension = ".yaml"
		else:
			extension = os.path.splitext(ai_model_structure.name)[1]
			load_file(ai_model.ai_model_structure, provider, model_id, STRUCTURE_NAME+extension)
	else:
		extension = os.path.splitext(model.name)[1]

	load_file(ai_model.requirements, provider, model_id, REQUIREMENTS_NAME)
	if preprocess_code != "":
		load_file(ai_model.preprocess_code, provider, model_id, PREPROCESS_NAME)
	if postprocess_code != "":
		load_file(ai_model.postprocess_code, provider, model_id, POSTPROCESS_NAME)
	print("Executing script...")
	script_path = os.environ.get('DEPLOY_SCRIPT_PATHV4')
	server_password = os.environ.get('SERVER_PASSWORD')
	subprocess.call("sshpass -p " + server_password + " ssh -o StrictHostKeyChecking=no " + ROOT + "@" + OVH_IP + " docker kill v4_" + str(model_id), shell=True)
	subprocess.call("sshpass -p " + server_password + " ssh -o StrictHostKeyChecking=no " + ROOT + "@" + OVH_IP + " docker container rm v4_" + str(
			model_id), shell=True)

	subprocess.call("sshpass -p " + server_password + " ssh -o StrictHostKeyChecking=no " + ROOT + "@" + OVH_IP
					+ " \"" + script_path + " " + str(provider.id) + " " +
					str(model_id) + " " + library + " " + extension[1:] + " \"", shell=True)
	print("Model " + str(model_id) + " deployed.")


def add_months(sourcedate, months):
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month // 12
	month = month % 12 + 1
	day = min(sourcedate.day, calendar.monthrange(year,month)[1])
	return datetime.date(year, month, day)