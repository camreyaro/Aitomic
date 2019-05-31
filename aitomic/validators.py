import os
from django.core.exceptions import ValidationError
import datetime

def validate_file_image_extension(value):
	ext = os.path.splitext(value.name)[1]  # [0] returns path + filename
	valid_extensions = ['.png', '.jpg']
	if not ext.lower() in valid_extensions:
		raise ValidationError(u'Images must be in PNG or JPG format.')


def validate_file_json_extension(value):
	ext = os.path.splitext(value.name)[1]  # [0] returns path + filename
	valid_extensions = ['.json']
	if not ext.lower() in valid_extensions:
		raise ValidationError(u'Must be a JSON.')

def validate_file_json_yaml_extension(value):
	ext = os.path.splitext(value.name)[1]  # [0] returns path + filename
	valid_extensions = ['.json', '.yaml']
	if not ext.lower() in valid_extensions:
		raise ValidationError(u'Must be a JSON or YAML.')


def only_past(date):
	if date > datetime.datetime.now().date():
		raise ValidationError("Birth date cannot be in the future")


def only_present_future(date):
	if date < datetime.datetime.now().date():
		raise ValidationError("Date cannot be past")


def validate_file_zip_extension(value):
	ext = os.path.splitext(value.name)[1]  # [0] returns path + filename
	valid_extensions = ['.zip']
	if not ext.lower() in valid_extensions:
		raise ValidationError(u'Must be a zip.')


def validate_file_txt_extension(value):
	ext = os.path.splitext(value.name)[1]  # [0] returns path + filename
	valid_extensions = ['.txt']
	if not ext.lower() in valid_extensions:
		raise ValidationError(u'Must be a txt.')


def validate_file_h5_extension(value):
	ext = os.path.splitext(value.name)[1]  # [0] returns path + filename
	valid_extensions = ['.h5']
	if not ext.lower() in valid_extensions:
		raise ValidationError(u'Must be a h5.')


def validate_file_py_extension(value):
	ext = os.path.splitext(value.name)[1]  # [0] returns path + filename
	valid_extensions = ['.py']
	if not ext.lower() in valid_extensions:
		raise ValidationError(u'Must be python file (.py).')


def validate_preprocess_code(value):
	f = value.open(mode='rb')
	code = f.read()
	if 'def preprocess(data):' not in str(code):
		raise ValidationError(u'Preprocess code is not correct.')


def validate_postprocess_code(value):
	f = value.open(mode='rb')
	code = f.read()
	if 'def postprocess(data):' not in str(code):
		raise ValidationError(u'Postprocess code is not correct.')
