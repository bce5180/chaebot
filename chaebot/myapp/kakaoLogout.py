from django.contrib.auth import logout


def force_logout(request):
    logout(request)
    return HttpResponseRedirect("/accounts/logout")
