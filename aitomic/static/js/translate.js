function changeLanguage(language) {
	document.getElementById("form_language_lang").value=language;
	document.getElementById("form_language").submit();
};

function getLanguageToUse() {
	var supportedLanguages = [
			"en", "es"
	];
	var language = getCookie("django_language");
	for ( var int = 0; int < supportedLanguages.length; int++) {
		if (language === supportedLanguages[int]) { return supportedLanguages[int]; }
	}
	return "en";
};

function getCookie(cname) {
	var name = cname + "=";
	var decodedCookie = decodeURIComponent(document.cookie);
	var ca = decodedCookie.split(';');
	for ( var i = 0; i < ca.length; i++) {
		var c = ca[i];
		while (c.charAt(0) == ' ') {
			c = c.substring(1);
		}
		if (c.indexOf(name) == 0) { return c.substring(name.length, c.length); }
	}
	return null;
};
