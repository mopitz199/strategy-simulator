from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader


def index(request):
    template = loader.get_template("landing_page/index.html")
    context = {
        "my_name": "Max",
    }
    return HttpResponse(template.render(context, request))