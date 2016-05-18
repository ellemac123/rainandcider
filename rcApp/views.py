from django.shortcuts import render_to_response
from django.shortcuts import redirect, render


def home(request):
     if request.method == 'POST':
          return redirect('openshift:detail')

     return render_to_response('home/home.html')


def detail(request):
     return render(request, 'country/detail.html')
