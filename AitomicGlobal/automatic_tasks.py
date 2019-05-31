from apscheduler.schedulers.background import BackgroundScheduler
from aitomic.models import AIModel, Profile
import datetime
import subprocess
import os

ROOT = "root"
OVH_IP = "54.38.65.178"
scheduler = BackgroundScheduler()

# This file has the definition of the tasks (jobs) that must be executed automatically.
# The moment can be defined by a cron or an interval of time, like the following
# examples specify.
# The scheduler queue is saved in RAM memory.
# The ID of each job must be unique.

# This job is executed each 10 seconds.
# @scheduler.scheduled_job("interval", seconds=10, id="intervaltestjob")
# def test_job():
#     print("I'm a test job!")


# This job is executed each day at 00:05.
# @scheduler.scheduled_job("cron", hour=0, minute=5, id="crontestjob")
# def test_job():
#     print("I'm a test job!")


# Every day at 00:05 deletes the models that have the deletion_date for today.
@scheduler.scheduled_job("cron", hour=0, minute=10, id="deletemodel")
def delete_models_marked():
	print("Deleting models")
	today = datetime.datetime.now()
	models_marked_for_deletion = AIModel.objects.filter(deletion_date=today)

	for model in models_marked_for_deletion:
		print("Going to delete model " + model.__str__())
		model_id = model.id
		provider = model.provider
		model.delete()
		server_password = os.environ.get('SERVER_PASSWORD')
		subprocess.call(
			"sshpass -p " + server_password + " ssh -o StrictHostKeyChecking=no " + ROOT + "@" + OVH_IP + " docker kill v2_" + str(
				model_id), shell=True)
		
		subprocess.call(
			"sshpass -p " + server_password + " ssh -o StrictHostKeyChecking=no " + ROOT + "@" + OVH_IP + " docker image rm -f " + str(
				model_id), shell=True)
		subprocess.call(
			"sshpass -p " + server_password + " ssh -o StrictHostKeyChecking=no " + ROOT + "@" + OVH_IP
			+ " rm -rf /root/aitomic_files/"+str(provider.id) +"/"+ str(model_id), shell=True)


@scheduler.scheduled_job("cron", hour=0, minute=1, id="deleteaccount")
def remove_account_marked():
	print("Deleting account")
	today = datetime.datetime.now()
	accounts_marked = Profile.objects.filter(deletion_date=today)

	for account in accounts_marked:
		print("Deleting account " + account.__str__())
		account.user.delete()


# This starts the scheduler
scheduler.start()
