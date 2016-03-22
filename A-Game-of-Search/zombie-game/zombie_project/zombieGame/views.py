import user
from models import UserProfile
from django.shortcuts import render, render_to_response
from forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from engine.main import show_game_screen
from engine.game import Game

#Homepage view
def index(request):
    return render(request, 'zombieGame/index.html')

#Login view
def login(request):
    context_dict = {'boldmessage': "login"}
    return render(request, 'zombieGame/login.html', context_dict)

#Profile view, requires user to be logged in
@login_required
def profile(request):
    context = RequestContext(request)
    profile = request.user.userprofile
    kills = request.user.userprofile.kills
    days = request.user.userprofile.days
    people = request.user.userprofile.people
    picture = request.user.userprofile.picture
    context_dict = {'profile': profile, 'kills': kills,'days': days, 'people':people, 'picture':picture}
    return render_to_response('zombieGame/profile.html', context_dict, context)
#def start_game(request):

#need to add ammo, partysize, days

#In this view we create a context_dict variable, which we can alter what is outputted to the game.html
def fill_dict(g):

    if g.game_state == 'STREET':
        context_dict = {'street': g.street, 'house_list': g.street.house_list, 'current_house':g.street.get_current_house(), 'turn': g.turn_options(),
                        'house_num': ['house_no']}
        return context_dict

        i=0
        for i in g.street.house_list:
            context_dict['house_no'].append(i)
            i += 1


    elif g.game_state == 'HOUSE':
        context_dict = {'house': g.street.get_current_house(),'room': g.street.get_current_house().get_current_room()}
        return context_dict

    elif g.game_state == 'ZOMBIE':
        context_dict = {'street': g.street, 'house_list': g.street.house_list,
                        'current_house':g.street.get_current_house(),
                        'current_room':g.street.get_current_house().get_current_room(),
                        'zombies': g.street.get_current_house().current_room.zombies}
        return context_dict


def turn(user, turn, value=None):
    if g.take_turn(turn) == 'WAIT':
        return game(request)
    elif g.take_turn(turn) == 'ENTER':
        context_dict = {'user': user }
        return context_dict
    #not working

#The main game view, requires user to be logged in
@login_required
def game(request):
    g = Game()
    g.start_new_day()
    context_dict=fill_dict(g)
    return render(request, 'zombieGame/game.html', context_dict)

#Leaderboards view, requires user to be logged in
@login_required
def leaderboard(request):
     num = [1,2,3,4,5,6,7,8,9,10]
     kills = UserProfile.objects.order_by('-kills')[:10]
     days = UserProfile.objects.order_by('-days')[:10]
     context_dict = {'index':num, 'kills':kills, 'days':days}
     return render(request, 'zombieGame/leaderboard.html', context_dict)

#Register view
def register(request):

    registered = False

    if request.method == 'POST':

        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # profile.user.kills = 0
            # profile.user.survival = 0

            profile.save()

            registered = True

        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
            'zombieGame/register.html',
            {'user_form': user_form, 'profile_form': profile_form, 'registered': registered} )

#Login view
def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                auth_login(request, user)
                return HttpResponseRedirect('/zombieGame/profile/')
            else:
                return HttpResponse("Your account is disabled.")
        else:
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, 'zombieGame/login.html', {})

#Logout view
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/zombieGame/')