from __future__ import unicode_literals
from django.db import models
from django.contrib import messages
from datetime import date, datetime
from django.db.models import Count
import re
import bcrypt

email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
name_regex = re.compile(r'^[a-zA-Z0-9]{3,}$')

class UserManager(models.Manager):
    def validate(self, postData):
        count = 0
        errors = []

        if not name_regex.match(postData['name']):
            errors.append("Name must be at least 3 characters and composed of only letters and numbers")
            count += 1
        if not name_regex.match(postData['alias']):
            errors.append("Alias must be at least 3 characters and composed of only letters and numbers")
            count += 1
        if len(self.filter(alias=postData['alias'])) > 0:
            errors.append("Registration is invalid. Alias is already registered!")
            count += 1
        if not email_regex.match(postData['email']):
            errors.append("Email not valid. Please use name@host.com format")
            count += 1
        if len(User.objects.filter(email = postData['email'])) > 0:
            errors.append("Email in use. Please choose another")
            count += 1
        if postData['pass1'] != postData['pass2']:
            errors.append("Passwords do not match")
            count += 1
        if len(postData['pass1']) | len(postData['pass2']) < 7:
            errors.append("Password must be at least 8 characters")
            count += 1
        try:
            bday = datetime.strptime(postData['bday'], '%Y-%m-%d')
            if bday >= datetime.now():
                errors.append("Invalid: Birthday in the future")
                count += 1
        except:
            errors.append('Missing birthday')
            count += 1

        if count > 0:
            return (False, errors)
        else:
            password = postData['pass1']
            pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

            newuser= User.objects.create(name = postData['name'], alias = postData['alias'], pw_hash = pw_hash, email = postData['email'], bday = postData['bday'])
            return (True, newuser)

    def login(self, postData):
        count = 0
        errors = []
        user = User.objects.filter(email = postData['lemail'])
        if len(user) < 1:
            errors.append("Not a registered Email")
            count +=1
        if count > 0:
            return (False, errors)

        else:
            if bcrypt.hashpw(postData['lpassword'].encode(), user[0].pw_hash.encode()) == user[0].pw_hash:
                return (True, user[0])
            else:
                errors.append('Password does not match')
                return (False, errors)

class PokeManager(models.Manager):
    def poking(self, targetid, user):
        try:
            print "here we go"
            currentuser = User.objects.get(id=user)
            poke = User.objects.get(id=targetid)
            print "almost there"
            Poke.objects.create(poker=currentuser, poked=poke)
            print "ok"
            return (True, 'You poked someone!')
        except:
            print "no good"
            return (False, 'Something went wrong')

class User(models.Model):
    name = models.CharField(max_length = 100)
    alias = models.CharField(max_length = 100)
    pw_hash = models.CharField(max_length = 250)
    bday = models.DateField(auto_now = False, blank = True)
    email = models.CharField(max_length = 100)
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now =True)
    objects = UserManager()

class Poke(models.Model):
    poker = models.ForeignKey(User, related_name='pokewriter')
    poked = models.ForeignKey(User, related_name='poketarget')
    created_at = models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now =True)
    objects = PokeManager()
