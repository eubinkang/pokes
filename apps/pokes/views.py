from django.shortcuts import render, redirect
from .models import User, Poke
from django.contrib import messages

def index(request):
    if "id" not in request.session:
        request.session['id'] = ""
    return render(request, 'pokes/index.html')

def register(request):
    if request.method == "GET":
        return redirect('/')

    user = User.objects.validate(request.POST)

    if user[0] == True:
        request.session['id'] = user[1].id
        return redirect('/pokes')
    else:
        for errors in user[1]:
            messages.error(request, errors)
        return redirect('/')

def login(request):
    if request.method == "GET":
        return redirect('/')

    else:
        user = User.objects.login(request.POST)
        if user[0] == True:
            request.session['id'] = user[1].id
            return redirect('/pokes')
        else:
            for errors in user[1]:
                messages.error(request, errors)
            return redirect('/')

def pokes(request):
    if "id" not in request.session:
        return redirect('/')

    try:
        currentuser = User.objects.get(id=request.session['id'])
        userlist = User.objects.all().exclude(id=request.session['id'])
        context = {
            "user": currentuser,
            "trap": Poke.objects.all().filter(poked=currentuser),
            "trap2": Poke.objects.all().exclude(poked=currentuser),
            "userlist": userlist
            }
        return render(request, 'pokes/pokes.html', context)
    except:
        context = {
            "user": currentuser
            }
        return render(request, 'pokes/pokes.html', context)


def poked(request, targetid):
    if "id" not in request.session:
        return redirect('/')

    try:
        poking = Poke.objects.poking(targetid, request.session['id'])
        if poking[0] == True:
            print "did something happen"
            return redirect('/pokes')
    except:
        messages.error(request, "Something went wrong. Try again later")
        return redirect('/')




def logout(request):
    request.session.pop('id')
    return redirect('/')
