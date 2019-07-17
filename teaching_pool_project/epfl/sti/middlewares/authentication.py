import logging
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import redirect
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

LOGIN_EXEMPT_URLS = [re.compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    LOGIN_EXEMPT_URLS += [re.compile(url)
                          for url in settings.LOGIN_EXEMPT_URLS]


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        logger.debug('LoginRequiredMiddleware initialized')

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user')
        path = request.path_info.lstrip('/')

        if not request.user.is_authenticated:
            if not any(url.match(path) for url in LOGIN_EXEMPT_URLS):
                return redirect(settings.LOGIN_URL)


class ImpersonationMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        logger.debug("ImpersonationMiddleware initialized")

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user')

        # Check if we want to impersonate someone else
        username_to_impersonate = request.GET.get('impersonate', None)
        if username_to_impersonate:
            logger.info("trying to impersonate {}", username_to_impersonate)

            if not request.user.is_superuser:
                logger.warning(
                    "The currently logged in user ({}) is not a super user.")
            else:
                logger.info("currently logged in user: {}",
                            request.user.username)

                try:
                    User = get_user_model()
                    user_to_impersonate = User.objects.get(
                        username=username_to_impersonate)
                    if user_to_impersonate and user_to_impersonate != request.user:
                        original_username = request.user.username
                        logout(request)
                        login(request, user_to_impersonate,
                              backend='django.contrib.auth.backends.ModelBackend')
                        request.session['original_username'] = original_username

                        logger.info(
                            request, "Successfully impersonated person.")
                        messages.info(request, mark_safe("<i class='fas fa-info-circle'></i>&nbsp;Current user switched to {} {}".format(
                            user_to_impersonate.first_name, user_to_impersonate.last_name)))
                except Exception as ex:
                    logger.error(ex)
                    messages.error(request, mark_safe(
                        "<i class='fas fa-exclamation-circle'></i>&nbsp;Unable to switch user. Please check the username you want to use."))

        # Check if the we want to go back to the 'normal' user
        want_to_release = request.GET.get('release_person', None)
        if want_to_release is not None:
            logger.info("Releasing the impersonation")
            original_username = request.session.get('original_username', None)
            if original_username:
                User = get_user_model()
                original_user = User.objects.get(username=original_username)
                logout(request)
                login(request, original_user,
                      backend='django.contrib.auth.backends.ModelBackend')
                messages.info(request, mark_safe("<i class='fas fa-info-circle'></i>&nbsp;Current user switched to {} {}".format(
                            original_user.first_name, original_user.last_name)))
                try:
                    del request.session['original_username']
                except KeyError:
                    pass
            else:
                logger.error(
                    "Unable to revert to the original username since it is not known")
