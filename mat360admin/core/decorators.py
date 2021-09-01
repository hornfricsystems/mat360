from django.shortcuts import redirect

from mat360admin.models import Mat360SystemUsers


def is_mat360admin(func):
    def wrap(request, *args, **kwargs):
        if Mat360SystemUsers.objects.filter(is_superuser=True):
            return func(request, *args, **kwargs)

        else:
           pass

    return wrap