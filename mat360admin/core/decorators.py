from django.shortcuts import redirect

from mat360admin.models import Mat360SystemUsers


def is_mat360admin(func):
    def wrap(request, *args, **kwargs):
        if Mat360SystemUsers.objects.filter(is_superuser=True):
            return func(request, *args, **kwargs)
        else:
           pass

    return wrap
def prevent_unauthorized_access(function):
    def wrap(request, *args, **kwargs):
        user_type = Mat360SystemUsers.objects.get(authenticating_user=request.user)

        if user_type.is_superuser:
            return function(request,*args,**kwargs)
        else:
            return redirect('home:login_applicant')
    return wrap

def user_is_administrator(func):
    def wrap(request,*args,**kwargs):
        if request.user.is_superuser:
            return func(request,*args,**kwargs)
        else:
            return redirect('mat360admin:admin-login')
    return wrap
def saccoManagerRequired(func):
    def wrap(request,*args,**kwargs):
        if request.user.is_staff and request.user.is_saccomanager:
            return func(request, *args, **kwargs)
        else:
            return redirect('mat360admin:admin-login')
    return wrap
def StageControllerRequired(func):
    def wrap(request,*args,**kwargs):
        if request.user.is_stagecontroller:
            return func(request, *args, **kwargs)
        else:
            return redirect('mat360admin:admin-login')
    return wrap