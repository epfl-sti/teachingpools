# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render

from django.http import HttpResponse, HttpResponseRedirect

from .forms import NameForm

def index(request):
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
