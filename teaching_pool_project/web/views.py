# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.conf import settings

from django.http import HttpResponse, HttpResponseRedirect

from .forms import NameForm

def index(request):
    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

    if request.method== 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/')
    else:
        form = NameForm()

    context = {
        'form': form
    }
    return render(request, 'web/index.html', context)
