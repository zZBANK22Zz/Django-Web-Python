from django.shortcuts import render, redirect

def handler404(request, exception):
    return render(request, 'myapp/404errorPage.html')
