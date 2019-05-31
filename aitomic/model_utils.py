def user_directory_path(instance, filename):
	"""
	This function sets where a file will be saved
	:param instance:
	:param filename: name of the file
	:return: file folder
	"""

	return "user_{0}/{1}".format(instance.user.id, filename)
