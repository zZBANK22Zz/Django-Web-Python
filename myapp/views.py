import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from linebot import LineBotApi
from linebot.models import TextSendMessage
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator

# Create your views here.
def addProduct(request):

    if request.method == 'POST':
        data = request.POST.copy()
        title = data.get('title')
        description = data.get('description')
        price = data.get('price')
        quantity = data.get('quantity')
        instock = data.get('instock')

        new = Product()
        new.title = title
        new.description = description
        new.price = price
        new.quantity = quantity
        if instock == "instock":
            new.instock = True
        else:
            new.instock = False
        
        if 'picture' in request.FILES:
            file_image = request.FILES['picture']
            file_image_name = file_image.name.replace(' ', '')  # delete space in file name
            # File system: from django.core.files.storage import FileSystemStorage
            fs = FileSystemStorage(location='media/product')
            filename = fs.save(file_image_name, file_image)
            upload_file_url = fs.url(filename)
            print('Picture url :', upload_file_url)
            new.picture = 'product' + upload_file_url[6:]

        if 'specfile' in request.FILES:
            file_specfile = request.FILES['specfile']
            file_specfile_name = file_specfile.name.replace(' ', '')  # delete space in file name
            # FileSystemStorage: from django.core.files.storage import FileSystemStorage
            fs = FileSystemStorage(location='media/specfile')
            filename = fs.save(file_specfile_name, file_specfile)
            upload_file_url = fs.url(filename)
            print('Specfile url :', upload_file_url)
            new.specfile = 'specfile' + upload_file_url[6:]

        new.save()

    return render(request, 'myapp/addproduct.html')

def actionPage(request, cid):
    # cid = contactlist ID
    context = {}
    contact = contactList.objects.get(id=cid)
    context['contact'] = contact

    try:
        action = Action.objects.get(contactList=contact)
        context['action'] = action
    except:
        pass

    if request.method == 'POST':
        data = request.POST.copy()
        actiondetail = data.get('actiondetail')

        if 'save' in data:
            try:
                check = Action.objects.get(contactList=contact)
                check.actionDetail = actiondetail
                check.save()
                context['action'] = check
            except:
                new = Action()
                new.contactList = contact
                new.actionDetail = actiondetail
                new.save()

        elif 'delete' in data:
            try:
                contact.delete()
                return redirect('showcontact-page')
            except:
                pass

        elif 'complete' in data:
            contact.complete = True
            contact.save()
            return redirect('showcontact-page')

    return render(request, 'myapp/action.html', context)

@login_required(login_url='/login')
def showContact(request):
    allcontact = contactList.objects.all()
    context = {'contact' : allcontact}
    return render(request, 'myapp/showcontact.html', context)

def userRegist(request):
    context = {}

    if request.method == 'POST':
        data = request.POST.copy()
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        repassword = data.get('repassword')

        try:
            # Check if username already exists
            User.objects.get(username=username)
            context['message'] = "Username duplicate"
        except:
            # Create a new user
            newuser = User()
            newuser.username = username
            newuser.first_name = firstname
            newuser.last_name = lastname
            newuser.email = email

            if password == repassword:
                # Set password securely
                newuser.set_password(password)
                newuser.save()

                # Create user profile
                newprofile = Profile()
                newprofile.user = User.objects.get(username=username)
                newprofile.save()

                context['message'] = "Register complete."
            else:
                context['message'] = "Password or re-password is incorrect."

    return render(request, 'myapp/register.html', context)

def userProfile(request):
    context = {}
    userprofile = Profile.objects.get(user=request.user)
    context['profile'] = userprofile
    return render(request, 'myapp/profile.html', context)

def editProfile(request):
    context = {}
    if request.method == 'POST':
        data = request.POST.copy()
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Get the current user
        current_user = User.objects.get(id=request.user.id)
        current_user.first_name = firstname
        current_user.last_name = lastname
        current_user.username = username
        current_user.email = email
        current_user.set_password(password)
        current_user.save()

        try:
            # Re-authenticate user after changing password
            user = authenticate(username=current_user.username,
                                password=password)
            login(request, user)
            return redirect('home-page')
        except:
            context['message'] = "Edit profile failed."

    return render(request, 'myapp/editprofile.html', context)

def userLogin(request):
    context = {}
    
    if request.method == 'POST':
        data = request.POST.copy()
        username = data.get('username')
        password = data.get('password')
        
        try:
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home-page')
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
    product_per_page = 3
    paginator = Paginator(allproduct, product_per_page)
    page = request.GET.get('page')
    allproduct = paginator.get_page(page)

    context = {'allproduct': allproduct}

    # 1 row 3 cols
    allrow = []
    row = []
    for i, p in enumerate(allproduct):
        if i % 3 == 0:
            if i != 0:
                allrow.append(row)
            row = []
            row.append(p)
        else:
            row.append(p)
    allrow.append(row)
    context['allrow'] = allrow

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
