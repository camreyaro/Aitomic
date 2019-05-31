from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .validators import *
from django.utils.encoding import force_bytes, force_text
from django.utils.translation import ugettext_lazy as _
from .models import *
from AitomicGlobal import settings

input_type_choices = (("Image", _("Image")), ("Text", _("Text")), ("Array of numbers", _("Array of numbers")), ("Number", _("Number")),
						("Audio", _("Audio")), ("Video", _("Video")))
library_choices = (("Keras", "Keras"), ("Scikit-Learn", "Scikit-Learn"))


class SignUpForm(UserCreationForm):
	birth_date = forms.DateField(required=False, help_text='Required. Format YYYY-MM-DD', validators=[only_past], label=_('Birth date'))
	first_name = forms.CharField(max_length=30, required=True, label=_('First name'))
	last_name = forms.CharField(max_length=30, required=True, label=_('Last name'))
	email = forms.EmailField(max_length=254, help_text=_('Required. Inform a valid email address.'), label=_('Email'))
	photo = forms.CharField(required=False, label=_('Profile Picture'))
	description = forms.CharField(max_length=300, required=False, widget=forms.Textarea(attrs={'placeholder': _('Introduce yourself')}), label=_('Description'))

	class Meta:
		model = User
		fields = (
			'username', 'birth_date', 'first_name', 'last_name', 'photo', 'email', 'description', 'password1', 'password2',)

class ChangePasswordForm(PasswordChangeForm):

	def __init__(self,request):
		if request.POST:
			super(PasswordChangeForm, self).__init__(request.user, request.POST)
		else:
			super(PasswordChangeForm, self).__init__(request.user)
		self.fields['old_password'].required = False
		self.fields['new_password1'].required = False
		self.fields['new_password2'].required = False
		self.fields['old_password'].widget.attrs.update(autofocus=False)
		self.fields['new_password1'].widget.attrs.update(autofocus=False)
		self.fields['new_password2'].widget.attrs.update(autofocus=False)

	class Meta:
		model = User
		fields = ('old_password', 'new_password1', 'new_password2',)


class AIModelForm(forms.Form):
	name = forms.CharField(label=_('Name'), max_length=100)
	general_description = forms.CharField(label=_("Description"), max_length=500, widget=forms.Textarea(attrs={'placeholder': _('Describe your model in a few words')}))
	image = forms.ImageField(label=_("Image"), validators=[validate_file_image_extension], required=False)  # We set this required to false and check image is set in controller since it's neccesary to edit a model
	input_example = forms.FileField(label=_("Input example file"), max_length=2000, required=False,
									validators=[validate_file_json_extension])
	input_example_text = forms.CharField(label=_("Input example text"), max_length=2000, widget=forms.Textarea(attrs={'placeholder': _('Write down the input example')}),
										 required=False)
	input_type = forms.ChoiceField(label=_("Input type"), required=True, choices=input_type_choices)
	output_example = forms.FileField(label=_("Output example file"), max_length=2000, required=False,
									 validators=[validate_file_json_extension])
	output_example_text = forms.CharField(label=_("Output example text"), max_length=2000, widget=forms.Textarea(attrs={'placeholder': _('Write the output example')}),
										  required=False)
	output_type = forms.ChoiceField(label=_("Output type"), required=True, choices=input_type_choices)
	ai_model_structure = forms.FileField(label=_("Model structure"), max_length=200000,
										 validators=[validate_file_json_yaml_extension], required=False)  # We set this required to false and check structure is set in controller since it's neccesary to edit a model
	weights = forms.FileField(label=_("Model weights"), max_length=5000000, validators=[validate_file_h5_extension], required=False)  # We set this required to false and check weight file is set in controller since it's neccesary to edit a model
	model = forms.FileField(label=_("Entire model"), max_length=5000000, required=False)
	library = forms.ChoiceField(label=_("Library"), required=True, choices=library_choices)
	auxiliar_files = forms.FileField(label=_("Auxiliar files"), max_length=20000, required=False,
									 validators=[validate_file_zip_extension])
	requirements = forms.FileField(label=_("Requirements file"), max_length=2000, required=False,
								   validators=[validate_file_txt_extension])
	requirements_text = forms.CharField(label=_("Requirements text"), max_length=2000, widget=forms.Textarea(attrs={'placeholder': _('Paste your requirements.txt file')}),
										required=False)
	technical_description = forms.CharField(label=_("Technical description"), max_length=3000, widget=forms.Textarea(attrs={'placeholder': _('Give some technical details')}))
	preprocess_code = forms.FileField(label=_("Preprocess code file"), max_length=5000000, required=False,
									  validators=[validate_file_py_extension, validate_preprocess_code])
	preprocess_code_text = forms.CharField(label=_("Preprocess code text"), max_length=100000, widget=forms.Textarea(attrs={'placeholder': _('Paste your preprocess function')}),
										   required=False)
	postprocess_code = forms.FileField(label=_("Postprocess code file"), max_length=5000000, required=False,
									   validators=[validate_file_py_extension, validate_postprocess_code])
	postprocess_code_text = forms.CharField(label=_("Postprocess code text"), max_length=100000, widget=forms.Textarea(attrs={'placeholder': _('Paste your preprocess function')}),
											required=False)
	price_hundred_calls = forms.FloatField(label=_("Price per 100 calls (€)"), min_value=0.)
	tags = forms.CharField(label=_("Tags"), max_length=200, required=False)
	measure = forms.CharField(label=_("Measure"), max_length=200)
	value = forms.FloatField(label=_("Value"))
	final_mode = forms.BooleanField(label=_("Final mode"), required=False)
	has_trial = forms.BooleanField(label=_("Free trial"), required=False)

	def save(self, user, image_encoded, input_example, output_example, ai_model_structure, requirements, preprocess_code,
				postprocess_code):

		ai_model = AIModel()
		ai_model.name = self.cleaned_data["name"]
		ai_model.general_description = self.cleaned_data["general_description"]
		ai_model.image = force_text(image_encoded)
		ai_model.input_example = force_text(input_example)
		ai_model.output_example = force_text(output_example)
		if ai_model_structure is not None:
			ai_model.ai_model_structure = force_text(ai_model_structure)

		ai_model.requirements = force_text(requirements)
		ai_model.technical_description = self.cleaned_data["technical_description"]
		ai_model.preprocess_code = force_text(preprocess_code)
		ai_model.price_hundred_calls = self.cleaned_data["price_hundred_calls"]
		ai_model.postprocess_code = force_text(postprocess_code)
		ai_model.tags = self.cleaned_data["tags"]
		ai_model.provider = user
		ai_model.input_type = self.cleaned_data["input_type"]
		ai_model.output_type = self.cleaned_data["output_type"]
		ai_model.final_mode = self.cleaned_data["final_mode"]
		ai_model.has_trial = self.cleaned_data["has_trial"]
		ai_model.deletion_date = None
		ai_model.save()
		return ai_model

	def update(self, model, measure, image_encoded, input_example, output_example, ai_model_structure, requirements, preprocess_code,
				postprocess_code, library):

		model.name = self.cleaned_data["name"]
		model.general_description = self.cleaned_data["general_description"]
		if image_encoded is not None:
			model.image = force_text(image_encoded)
		model.input_example = force_text(input_example)
		model.output_example = force_text(output_example)
		model.library = force_text(library)
		if ai_model_structure is not None:
			model.ai_model_structure = force_text(ai_model_structure)
		model.requirements = force_text(requirements)
		model.technical_description = self.cleaned_data["technical_description"]
		model.preprocess_code = force_text(preprocess_code)
		model.price_hundred_calls = self.cleaned_data["price_hundred_calls"]
		model.postprocess_code = force_text(postprocess_code)
		model.tags = self.cleaned_data["tags"]
		model.input_type = self.cleaned_data["input_type"]
		model.output_type = self.cleaned_data["output_type"]
		model.final_mode = self.cleaned_data["final_mode"]
		model.has_trial = self.cleaned_data["has_trial"]
		model.deletion_date = None
		measure.type = self.cleaned_data["measure"]
		measure.value = self.cleaned_data["value"]
		measure.save()
		model.save()
		return model


class UserProfileForm(forms.ModelForm):
	username = forms.CharField(max_length=20, required=True, disabled=True, label=_('Username'))
	first_name = forms.CharField(max_length=30, required=True, label=_('First name'))
	last_name = forms.CharField(max_length=30, required=True, label=_('Last name'))
	
	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name')

	def save(self, user):
		#user.username = self.cleaned_data.get('username')
		user.first_name = self.cleaned_data.get('first_name')
		user.last_name = self.cleaned_data.get('last_name')
		user.save()
		return user


class ProfileProfileForm(forms.ModelForm):
	
	birth_date = forms.DateField(help_text=_('Required. Format YYYY-MM-DD'), validators=[only_past], label=_('Birth date'))
	#email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.',)
	#photo = forms.URLField(max_length=250, required=False)
	photo = forms.ImageField(label=_("Profile picutre"), required=False)
	description = forms.CharField(max_length=300, required=False, widget=forms.Textarea(attrs={'placeholder': _('Introduce yourself')}) )

	class Meta:
		model = User
		fields = ('birth_date', 'photo', 'description')

	def save(self, user, image_encoded):
		user.profile.photo = image_encoded
		user.profile.birth_date = self.cleaned_data.get('birth_date')
		user.profile.description = self.cleaned_data.get('description')
		user.save()
		return user


class SearchModelForm(forms.Form):
	p_search = forms.CharField(required=False, label=_('Search'))
	min_price = forms.FloatField(required=False, label=_('Min price'))
	max_price = forms.IntegerField(required=False, label=_('Max price'))
	select_choice = (
		('', _('Default')), ('1', _('Price: Low-High'),), ('2', _('Price: High-low'),), ('3', _('Rating: Low-High')), ('4', _('Rating: High-Low')),
		('5', _('Name')), ('6', _('Author')),)
	select_order = forms.ChoiceField(widget=forms.Select, choices=select_choice, label=_('Order'))
	rating_choice = (('1', 1,), ('2', 2,), ('3', 3), ('4', 4), ('5', 5),)
	rating = forms.ChoiceField(widget=forms.RadioSelect, choices=rating_choice, label=_('Rating'))


class PaymentForm(forms.Form):
	quantity = forms.IntegerField(required=True,min_value=1,label=_("Quantity"),widget=forms.NumberInput(attrs={"id":'quantity'}))
	moment_to_use = forms.DateField(required=True, label=_("Moment"), widget=forms.DateInput(format=settings.DATE_INPUT_FORMATS), input_formats=settings.DATE_INPUT_FORMATS)

	def clean(self):
		cleaned_data = super(PaymentForm, self).clean()
		moment_to_use = cleaned_data.get('moment_to_use')
		#moment_to_use = datetime.datetime.strptime(moment_to_use, settings.DATE_INPUT_FORMATS).date()

		if moment_to_use < datetime.date.today():
			self._errors['moment_to_use'] = self.error_class([_('Date can not be past.')])

		return cleaned_data

class ApiModel(forms.Form):
	photo = forms.ImageField(label=_("Image"), required=False, validators=[validate_file_image_extension])
	manual_text = forms.CharField(label=_("Manual Text"), max_length=1000, widget=forms.Textarea, required=False)
	input_text = forms.FileField(label=_("Input Text File"), required=False)


class WriteCommentForm(forms.Form):
	text = forms.CharField(label=_('Text'), max_length=500)


class EditAIModelForm(forms.Form):
	name = forms.CharField(label=_('Name'), max_length=100)
	general_description = forms.CharField(label=_("Description"), max_length=500, widget=forms.Textarea(attrs={'placeholder': _('Describe your model in a few words')}))
	image = forms.ImageField(label=_("Image"), validators=[validate_file_image_extension], required=False)
	technical_description = forms.CharField(label=_("Technical description"), max_length=3000,  widget=forms.Textarea(attrs={'placeholder': _('Give some technical details')}))
	price_hundred_calls = forms.FloatField(label=_("Price per 100 calls (€)"), min_value=0.)
	tags = forms.CharField(label=_("Tags"), max_length=200, required=False)
	measure = forms.CharField(label=_("Measure"), max_length=200)
	value = forms.CharField(label=_("Value"), max_length=200)
	delete = forms.BooleanField(label=_("Delete"), required=False)

	def save(self, model, measure, image_encoded, deletion_date):
		model.name = self.cleaned_data["name"]
		model.general_description = self.cleaned_data["general_description"]
		if image_encoded is not None:
			model.image = force_text(image_encoded)
		model.technical_description = self.cleaned_data["technical_description"]
		model.price_hundred_calls = self.cleaned_data["price_hundred_calls"]
		model.tags = self.cleaned_data["tags"]
		model.deletion_date = deletion_date
		measure.type = self.cleaned_data["measure"]
		measure.value = self.cleaned_data["value"]
		measure.save()
		model.save()
		return model


class RevisionForm(forms.ModelForm):
	version = forms.CharField(label= _("Version"), max_length=10, required=True)
	photo = forms.ImageField(label= _("Photo"), required=False)
	description = forms.CharField(label= _("Description"),widget=forms.Textarea(attrs={'placeholder':_('Describe your changes')}), max_length=1500, required=True)
	description_es = forms.CharField(label= _("Spanish description"),widget=forms.Textarea(attrs={'placeholder':_('Describe your changes in Spanish')}), max_length=1500, required=True)

	class Meta:
		model = Revision
		fields = ('version', 'photo','description', 'description_es')


class VoteModelForm(forms.Form):
	rating_choice = (('1', 1,), ('2', 2,), ('3', 3), ('4', 4), ('5', 5),)
	rating = forms.ChoiceField(widget=forms.RadioSelect, choices=rating_choice, label=_('Vote'))
	class Meta:
		model = Vote
		fields = ('vote',)


class EarnBenefitsForm(forms.Form):
	paypal_email_1 = forms.EmailField(label=_("Email address of your PayPal account"),
										required=True, max_length=254)
	paypal_email_2 = forms.EmailField(label=_("Repeat the email address of your Paypal account"),
										required=True, max_length=254,)

	def clean(self):
		cleaned_data = super(EarnBenefitsForm, self).clean()
		email_1 = cleaned_data.get('paypal_email_1')
		email_2 = cleaned_data.get('paypal_email_2')

		if email_1 and email_2 and email_1 != email_2:
			self._errors['paypal_email_2'] = self.error_class([_('Emails do not match.')])
			del self.cleaned_data['paypal_email_2']

		return cleaned_data


class AlertForm(forms.Form):
	text = forms.CharField(required=True, widget=forms.Textarea)
