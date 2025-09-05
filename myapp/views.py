import os
from django.shortcuts import render
from django.http import HttpResponse
from linebot import LineBotApi
from linebot.models import TextSendMessage
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout

# Create your views here.

def showContact(request):
    allcontact = contactList.objects.all()
    context = {'contact' : allcontact}
    return render(request, 'myapp/showcontact.html', context)

def userLogin(request):
    context = {}
    
    if request.method == 'POST':
        data = request.POST.copy()
        username = data.get('username')
        password = data.get('password')
        
        try:
            user = authenticate(username=username, password=password)
            login(request, user)
        except:
            context['message'] = 'Invalid username or password!'
            
    return render(request, 'myapp/login.html', context)

@csrf_exempt
def line_webhook(request):
    if request.method != "POST":
        # Optional: return 200 so opening the URL in a browser doesn't 404/405
        return HttpResponse("OK", status=200)
    # For now, don’t validate signature; just acknowledge
    return HttpResponse("OK", status=200)
# Load LINE configs from .env
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "")
LINE_ADMIN_USER_IDS = [uid.strip() for uid in os.environ.get("LINE_ADMIN_USER_IDS", "").split(",") if uid.strip()]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN) if LINE_CHANNEL_ACCESS_TOKEN else None

def home(request):
    allproduct = Product.objects.all()
    context = {'pd' : allproduct}
    return render(request, 'myapp/home.html', context)

def contact(request):
    context = {}

    if request.method == 'POST':
        data = request.POST.copy()
        topic = data.get('topic')
        email = data.get('email')
        detail = data.get('detail')

        if not topic or not email or not detail:
            context['message'] = 'Please fill in all the fields!'
            return render(request, 'myapp/contact.html', context)

        # Save the record
        newRecord = contactList()
        newRecord.topic = topic
        newRecord.email = email
        newRecord.detail = detail
        newRecord.save()

        # Push LINE notification to admin(s)
        if line_bot_api and LINE_ADMIN_USER_IDS:
            message = (
                "✉️ New Contact Message\n"
                f"Topic: {topic}\n"
                f"Email: {email}\n"
                f"Detail: {detail}"
            )
            try:
                for admin_id in LINE_ADMIN_USER_IDS:
                    line_bot_api.push_message(admin_id, TextSendMessage(text=message))
            except Exception as e:
                print(f"[LINE push error] {e}")

        context['message'] = 'The message has been received!'

    return render(request, 'myapp/contact.html', context)

def home2(request):
    return HttpResponse("<h1>Hellow world2</h1>")

def aboutUs(request):
    return render(request, 'myapp/aboutus.html')