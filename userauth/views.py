from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import auth


def login(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            context['error'] = 'Пользователя с таким логином и паролем не существует.'
            return render(request, 'login.html', context)
    else:
        return render(request, 'login.html', context)


def logout(request):
    auth.logout(request)
    return redirect('/')
