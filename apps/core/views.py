from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render


def main(request):

    context = {}
    return render(request, 'main.html', context)