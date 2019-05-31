from django.db import models, transaction
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .model_utils import *
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
import datetime
from .views_utils import add_months

input_type_choices = (("Image", "Image"), ("Text", "Text"), ("Array of numbers", "Array of numbers"), ("Number", "Number"),
						("Audio", "Audio"), ("Video", "Video"))

library_choices = (("Keras", "Keras"), ("Scikit-Learn", "Scikit-Learn"))


class ModelBought(models.Model):
	moment = models.DateTimeField(auto_now_add=True)
	totalCalls = models.IntegerField()
	callsLeft = models.IntegerField()
	model = models.ForeignKey('AIModel', on_delete=models.CASCADE, null=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
	moment_to_use = models.DateField(null=False, blank=False)

	@property
	def ending_moment(self):
		return add_months(self.moment_to_use,1)

	@property
	def has_expired(self):
		return self.ending_moment < datetime.date.today()

	@property
	def callable(self):
		return self.moment_to_use <= datetime.date.today() and not self.has_expired


class Profile(models.Model):
	"""Class extending User model in order to add custom attributes"""

	user = models.OneToOneField(User, on_delete=models.CASCADE)
	birth_date = models.DateField(null=True, blank=True)
	# TODO not yet implemented
	photo = models.TextField(null=True)
	# TODO not yet implemented, take a look at https://github.com/stefanfoulis/django-phonenumber-field
	# TODO we can use the 'is_active' attr from User class as the 'banned' attribute, which denies login if is set to False
	# TODO we can use 'date_joined' attr from User class as the 'registerDate' attribute, it makes what we want
	email_confirmed = models.BooleanField(default=False)
	description = models.CharField(max_length=300, null=True)
	deletion_date = models.DateField(null=True, default=None)

	# modelsBought = models.ArrayModelField(model_container=ModelBought, default=[])

	def __str__(self):
		return self.user.first_name

	@receiver(post_save, sender=User)
	def create_user_profile(sender, instance, created, **kwargs):
		if created:
			Profile.objects.create(user=instance)

	@receiver(post_save, sender=User)
	def save_user_profile(sender, instance, **kwargs):
		instance.profile.save()


class Tag(models.Model):
	tag = models.CharField(blank=True, max_length=40)
	ai_model = models.ForeignKey('AIModel', on_delete=models.CASCADE)

	def __str__(self):
		return self.tag


class AIModel(models.Model):
	name = models.CharField(blank=False, max_length=100)
	general_description = models.TextField(blank=False)
	image = models.TextField()
	input_example = models.TextField()
	input_type = models.CharField(choices=input_type_choices, max_length=50)
	library = models.CharField(choices=library_choices, max_length=50)
	output_example = models.TextField()
	output_type = models.CharField(choices=input_type_choices, max_length=50)
	ai_model_structure = models.TextField()
	requirements = models.TextField(null=True, blank=True)
	#auxiliar_files = models.TextField(null=True, blank=True)
	technical_description = models.TextField(blank=False)
	preprocess_code = models.TextField(null=True)
	postprocess_code = models.TextField(null=True)
	api_url = models.URLField(blank=False)
	price_hundred_calls = models.FloatField(validators=[MinValueValidator(1.0)], default=1)
	monthly_calls = models.IntegerField(validators=[MinValueValidator(100)])
	rating = models.FloatField(default=0.)
	tags = models.CharField(max_length=200)
	date_created = models.DateField(auto_now_add=True)
	provider = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null= True)
	final_mode = models.BooleanField(default=False, null=False)
	has_trial = models.BooleanField(default=False, null=False)
	deletion_date = models.DateField(null=True,default=None)

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('model_detail', args=[str(self.id)])


class Measure(models.Model):
	ai_model = models.ForeignKey('AIModel', on_delete=models.CASCADE)
	type = models.CharField(blank=False, max_length=40)
	value = models.FloatField(null=False)

	def __str__(self):
		return self.type + " " + self.value.__str__()


class ApiCall(models.Model):
	#  apiCall_id = models.ObjectIdField()
	moment = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, null=True)
	model = models.ForeignKey('AIModel', on_delete=models.CASCADE, null=True)
	is_free = models.BooleanField(default=False, null=False)

	def __str__(self):
		return self.user.__str__() + " made an API call to model " + self.model.__str__() + " on " + self.moment.__str__()


class Payment(models.Model):
	orderID = models.CharField(null=False, unique=True, max_length=100, blank=False)  # PayPal's order ID
	moment = models.DateTimeField(auto_now_add=True)
	quantity = models.IntegerField(verbose_name=_("Quantity"))
	price = models.FloatField(null=False)
	reclaimed = models.BooleanField(default=False, null=False)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
	model = models.ForeignKey('AIModel', on_delete=models.CASCADE, null=False)

	def __str__(self):
		return self.user.__str__() + " paid " + self.price.__str__() + " to buy " + self.quantity.__str__() + " calls on model: " + self.model.__str__()

	def get_absolute_url(self):
		return reverse('model_detail', args=[str(self.model_id)])


class Vote(models.Model):
	#  vote_id = models.ObjectIdField()
	value = models.IntegerField()
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
	model = models.ForeignKey('AIModel', on_delete=models.CASCADE)

	def __str__(self):
		return self.user.__str__() +" voted "+self.value.__str__() + " on model: " + self.model.__str__()


class Comment(models.Model):

	text = models.TextField(blank=False)
	badge = models.BooleanField(default=False)# TODO if the user has bought the model show badge.
	model = models.ForeignKey('AIModel', on_delete=models.CASCADE, null=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.text


class Revision(models.Model):
	version=models.CharField(max_length=10)
	publication_date = models.DateField(null=True, blank=True, auto_now_add=True)
	photo = models.TextField(null=True)
	description = models.CharField(max_length=1500)
	description_es = models.CharField(max_length=1500)


	def __str__(self):
		return "version"+self.version.__str__() + "description" + self.description.__str__()


class ConcurrentModificationError(Exception):
	def __init__(self, model, pk):
		super(ConcurrentModificationError, self).__init__(
			"Concurrent modification on %s #%s" % (model, pk))
