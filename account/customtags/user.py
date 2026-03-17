from django import template

from django.conf import settings

register = template.Library()

@register.inclusion_tag('auth/customtags/usertoolbar.html')
def usertoolbar(request):
    
    return {
        'request': request,
        'AUTH_DEFAULT_HOME': settings.AUTH_DEFAULT_HOME,
        'AUTH_BACKOFFICE': settings.AUTH_BACKOFFICE,
        'AUTH_SELF_CREATE': settings.AUTH_SELF_CREATE,
        'AUTH_SELF_RECOVERY': settings.AUTH_SELF_RECOVERY,
        'AUTH_AUTO_ACTIVATE': settings.AUTH_AUTO_ACTIVATE
    }

def user(request):
    return {
        'request': request,
        'AUTH_DEFAULT_HOME': settings.AUTH_DEFAULT_HOME,
        'AUTH_BACKOFFICE': settings.AUTH_BACKOFFICE,
        'AUTH_SELF_CREATE': settings.AUTH_SELF_CREATE,
        'AUTH_SELF_RECOVERY': settings.AUTH_SELF_RECOVERY,
        'AUTH_AUTO_ACTIVATE': settings.AUTH_AUTO_ACTIVATE
    }