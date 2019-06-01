"""
Django settings for AitomicGlobal project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import os
from django.utils.translation import ugettext_lazy as _


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '3j%oi700k0!*x11zp0!^4*z630$ujh!i78x@fb$4i$!)7)#jcm'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

if DEBUG:
	MODEL_CONF_DIR = "/app/aitomic_files"  # BE CAREFUL WITH THIS PLS
	REMOTE_AITOMIC_FILES = "/root/aitomic_files"
else:
	MODEL_CONF_DIR = "/volume"  # TODO
	REMOTE_AITOMIC_FILES = "/root/aitomic_files"

# Application definition

INSTALLED_APPS = [
	'widget_tweaks',
	'bulma',
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'aitomic.apps.AitomicConfig',
	'social_django',
	'django_babel',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django_babel.middleware.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'AitomicGlobal.urls'

TEMPLATES = [
	{
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
		'DIRS': [os.path.join(BASE_DIR, 'templates'), os.path.join(BASE_DIR, 'aitomic/templates/aitomic')],
		'APP_DIRS': True,
		'OPTIONS': {
			'context_processors': [
				'django.template.context_processors.debug',
				'django.template.context_processors.request',
				'django.contrib.auth.context_processors.auth',
				'django.contrib.messages.context_processors.messages',
				'social_django.context_processors.backends',
				'social_django.context_processors.login_redirect',
				'django.template.context_processors.media',
				# 'django.core.context_processors.i18n',
				'django.template.context_processors.i18n'
			],
		},
	},
]

WSGI_APPLICATION = 'AitomicGlobal.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
	'default': {
		'ENGINE': 'djongo',
		'ENFORCE_SCHEMA': False,
		'NAME': 'aitomic',
		'HOST': 'mongodb://admin:QNSADg98NI@mongodb.aitomic.net/aitomic',
		'PORT': 27017,
		'SUPPORT_TRANSACTIONS': True,
		'TEST': {
			'NAME': 'testDB',
		}
	}
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
{
	'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
},
{
	'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
},
{
	'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
},
{
	'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
},
]

AUTHENTICATION_BACKENDS = (
'social_core.backends.open_id.OpenIdAuth',
'social_core.backends.google.GoogleOpenId',
'social_core.backends.google.GoogleOAuth2',
'django.contrib.auth.backends.ModelBackend',
)

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGES = (
('en', _('English')),
('es', _('Spanish'))
)
LANGUAGE_CODE = 'en-GB'

LOCALE_PATHS = (
os.path.join(BASE_DIR, 'aitomic\locale'),
)
TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_L10N = True

USE_TZ = True

DATE_INPUT_FORMATS = [
    '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%m/%d/%y', # '2006-10-25', '10/25/2006', '10/25/06'
    '%b %d %Y', '%b %d, %Y',            # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',            # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',            # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',            # '25 October 2006', '25 October, 2006'
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
PROJECT_DIR = os.path.dirname(__file__)
STATIC_ROOT = os.path.join(PROJECT_DIR, 'static/')
STATICFILES_DIRS = ('./aitomic/static',)

ATOMIC_REQUESTS = True

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

# Email config
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '138342920951-hr0elvqe6a3jmp203cs7g9ukd7efhman.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'cumtvNzXLKMzsJbzgUeMoTnD'

MODEL_CONF_URL = '/model_conf/'
MODEL_CONF_ROOT = os.path.join(MODEL_CONF_DIR, 'model_conf')

# Paypal conf
PAYPAL_CLIENT_ID = "AbKCB5kKU54ElBnXkoYn5vUt3PibBWee7LwpRPHHnA1HCzTvb-9XMdQzbHxzSJAfUV0mxXgwFhK2D2tx"
PAYPAL_CLIENT_SECRET = "EG_tdWaMbTwYy8Gk0BbbKcd0Tj_Uyos3z0yLy8H1RsYZoSN0OMJpoiUPNYjsC7AH47Pvk5d__U-EItvM"
PAYPAL_PAYOUT_URL = "https://api.sandbox.paypal.com/v1/payments/payouts"
PAYPAL_ACCESS_TOKEN_URL = "https://api.sandbox.paypal.com/v1/oauth2/token"

FREE_CALLS = 10
PERCENTAGE_FOR_PROVIDER = 0.95
