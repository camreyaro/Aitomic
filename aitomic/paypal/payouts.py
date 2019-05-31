import requests
from AitomicGlobal.settings import PAYPAL_PAYOUT_URL, PERCENTAGE_FOR_PROVIDER, PAYPAL_ACCESS_TOKEN_URL, \
	PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET
from aitomic.models import AIModel, Payment
from django.utils.translation import ugettext_lazy as _
import json
import time


def get_money_and_calls(user_id):
	total_money = 0.
	total_calls_sold = 0
	my_models = AIModel.objects.filter(provider=user_id)

	for model in my_models:
		payments = Payment.objects.filter(model=model.pk, reclaimed=False)
		for payment in payments:
			total_money = total_money + payment.price
			total_calls_sold = total_calls_sold + payment.quantity

	total_money = total_money * PERCENTAGE_FOR_PROVIDER

	return {'total_money': total_money, 'total_calls_sold': total_calls_sold}


def get_bearer_token():
	url = PAYPAL_ACCESS_TOKEN_URL  # https://api.sandbox.paypal.com/v1/oauth2/token
	headers = {'Accept': 'application/json', 'Accept-Language': 'en-US'}
	body = "grant_type=client_credentials"

	r = requests.post(url, auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET), data=body, headers=headers)

	response = r.content
	response_json = json.loads(response)
	access_token = response_json['access_token']

	return str(access_token)


def send_payout(amount, email, user_id):
	url = PAYPAL_PAYOUT_URL  # https://api.sandbox.paypal.com/v1/payments/payouts
	paypal_access_token = get_bearer_token()
	headers = {'content-type': 'application/json', 'authorization': 'Bearer ' + paypal_access_token}
	email_subject = _("You have a payout from Aitomic")
	email_message = _("You have received a payout from the sales of your models uploaded. Thank you for using Aitomic")
	note = _("Thanks for your collaboration with Aitomic.")
	# id-YY-MM-DD-HH-mm-ss
	date_string = time.strftime("%Y-%m-%d-%H-%M-%S")
	sender_batch_id = str(user_id) + "-" + date_string

	payload = {
		"sender_batch_header": {
			"sender_batch_id": sender_batch_id,
			"email_subject": str(email_subject),  # Casting to string because Python's JSON encoder
			"email_message": str(email_message)	 # doesn't know about ugettext_lazy
		},
		"items": [
			{
				"recipient_type": "EMAIL",
				"amount": {
					"value": amount,
					"currency": "EUR"
				},
				"note": str(note),
				"receiver": email
			}
		]
	}

	payload_json = json.dumps(payload)

	r = requests.post(url, headers=headers, data=payload_json)

	return r


def set_payments_reclaimed(user_id):
	my_models = AIModel.objects.filter(provider=user_id)

	for model in my_models:
		payments = Payment.objects.filter(model=model.pk, reclaimed=False)
		for payment in payments:
			payment.reclaimed = True
			payment.save()
