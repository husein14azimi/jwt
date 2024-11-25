<br></br>
<p style="text-align:center;">
IN THE NAME OF GOD
</p>

<p align="center">
lorem ipsum
</p>


<br></br>
<br></br>

# jwt project 💻

this is a simple django project with two web applications:
1. main app (core)
2. profile app (account)

> it is actually a template project for authenticating via jwt

technologies used in the project:
* RESTful apis
* (Authentication): `jwt` (as the authenticatoin backend) and `djoser` (for pre-written `views` and `urls`)
* (dev environment:) Visual Studio Code on Windows



# creating this project, step by step:

create a project named `core` and then rename the project to whatever you like. renaming the project is easier than renaming the main application of the project.

**note:** in this doc, in each file's code snippet, the full content of the file is typed; but in some cases (such as `settings.py`), only the code that should be modified is there.

#### editing the `core.settings`

register `core` as a web app in this project:
```
# core.settings

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]
```
if you're working on local host, write:
```
ALLOWED_HOSTS = ['127.0.0.1', 'localhost',]
```

you can also edit the time zone:
```
TIME_ZONE = 'Asia/Tehran'
```


### virtual environment
virtual environment is dependent on the address of its directory; that's why it is created after renaming the project. change `<the_name>` to your desired name:

```
python -m venv <the_name>
```

install django for your venv
```
pip install django
```

## the `user` model

extend the abstract user in the `core.models` so extra fields based on the project requirements can be added to the django base `User` model.

the `username` in this project has no place and the field required for login is `email`. to achieve that, the `username` field is set to `blank=True`. so far, `core.User` does not require any `username` field; but there is some code in the default django codes that still require `username` (which is the `UserManager`). we will change it and use it in the `core.User`.


```
# core.models

from django.db import models
from django.contrib.auth.models import AbstractUser  as BaseAbstractUser 
from django.contrib.auth.models import BaseUserManager
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    def create_user(self, email, phone_number, password=None, **extra_fields):
        """Create and return a 'User' with an email, phone number and password."""
        if not email:
            raise ValueError('The Email field must be set')
        if not phone_number:
            raise ValueError('The Phone number field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)  # Use set_password to hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, password=None, **extra_fields):
        """Create and return a superuser with an email, phone number and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, phone_number, password, **extra_fields)
    

class User(BaseAbstractUser ):
    username = models.CharField(max_length=255, unique=False, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(regex=r'^09\d{9}$', message="Phone number must start with 09 and be exactly 11 characters.")
    phone_number = models.CharField(validators=[phone_regex], max_length=11, unique=True)

    USERNAME_FIELD = 'email'
    
    REQUIRED_FIELDS = ['phone_number']

    objects = UserManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name}: {self.email}'
```


### admin-registering

we also register this specific `User` to the admin panel. since there are some modified fields in it, they have to be shown to django:

```
# core.admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'phone_number', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(User, UserAdmin)
```



add to the `core.settings`:
```
# core.settings

AUTH_USER_MODEL= 'core.User'
```

## migrating

maybe in the first migration, the `core` app is not recognized; therefore, it is recommended to run:
```
python manage.py makemigrations core
```

and then run the global migration:
```
python manage.py makemigrations
```
```
python manage.py migrate
```

#### creating a superuser

if in this step, the additional fields you have added to the `core.User` take part, then you have changed the *auth flow* successfully.
```
python manage.py createsuperuser
```
you can see/create users in the
```
localhost:8000/admin
```


## REST framework

install it first:
```
pip install djangorestframework
```
add it to the installed apps in the `core.settings`

```
# core.settings

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
]
```

now, you have rest framework in your project.

**map:**
there are two models in the auth flow: `core.User` and `account.Person`. one includes the required fields for authentication such as email, phone number, password; so it stays the same in each project; but the `account.Person` will have different fields based on the project's requirements. we will build do the stuff related to `core.User`, then build the `account.Person` and its configuration and at last, we will connect them together so the user does not need two different forms to update their profile. the `core.User` uses djoser for the view-writing to prevent over-coding and `account.Person` will need its serializers and views. to implement the connection between the two, one approach is developing a new serializer-view-url and the other one is to write the serializer-view for the `account.Person` in a way that fetches the data from `core.User`, combine them with the `account.Person` data and show them all together to the user.

therefore, there will be 3 steps:
1. creating the user model and its configurations
2. creating the person model and its configurations
3. connecting the two




### install djoser and jwt

run:
```
pip install djoser
```
```
pip install djangorestframework_simplejwt
```

register djoser as an app:
```
# core.settings

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'djoser',
    'core',
]
```

add the djoser url endpoints:
```
# core.urls

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]
```

set jwt as the authenticatoin backend:

```
# core.settings

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
```

and add:
```
# core.settings

SIMPLE_JWT = {
   'AUTH_HEADER_TYPES': ('JWT',),
}
```

or if you want more customized settings:
```
# core.settings

from datetime import timedelta

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    "ACCESS_TOKEN_LIFETIME": timedelta(days=3),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
}
```

i just thought that access token must be valid for 3 days. you can change it there 👆.



**map:** the `core.User` and auth configuration is implemented. now, we implement the `person`(profile) model.

**note:** to get the current user's data, use the url `auth/users/me`.
```
localhost:8000/auth/users/me/
```

**note:** you can get your `access` and `refresh` tokens using the url `auth/jwt/create`. to refresh the access token, use the url `auth/jwt/refresh` along with your **refresh token**. 


## `account` app and `Person` (profile) model

run:
```
python manage.py startapp account
```

in `core.urls`, add the url for account app:
```
# core.urls

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    
    path('account/', include('account.urls')),
]

```

create the `urls` file in the `account` app (does not include any urls for now):
```
# account.urls

urlpatterns = [

]
```

add it to the installed apps:
```
# core.settings

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',
    'account',
]
```

create the `person` model:
```
# account.models

from django.db import models
from django.conf import settings


gender_choices = (
    ('M', 'Male'),
    ('F', 'Female'),
)

class Person(models.Model):
    user = models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gender = models.CharField(max_length=1, choices=gender_choices, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True)

    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}: {self.user.email}'
```


(optional) register the `account.Person` for the `admin` panel:
```
# account.admin

from django.contrib import admin
from .models import Person

admin.site.register(Person)
```

run the migrations afterwise.


**note:** 
the following serializer is a complex serializer that combines the `User` and `Person` models. how? well, first it fetches the `User` data from the main app and then, combines it with the `Person` model.


write the needed serializer-view-url:



```
# account.serializers

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class CombinedUserPersonSerializer(serializers.ModelSerializer):
    bio = serializers.CharField(source='person.bio', allow_blank=True)
    birth_date = serializers.DateField(source='person.birth_date', allow_null=True)
    gender = serializers.CharField(source='person.gender', allow_null=True)
    updated_at = serializers.DateTimeField(source='person.updated_at', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'date_joined', 'last_login', 'bio', 'birth_date', 'gender', 'updated_at',]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login',]

    def update(self, instance, validated_data):
        person_data = {}
        for field in ['bio', 'birth_date', 'gender']:
            if field in validated_data:
                person_data[field] = validated_data.pop(field)

        super().update(instance, validated_data)

        if person_data:
            person = instance.person
            for attr, value in person_data.items():
                setattr(person, attr, value)
            person.save()

        return instance
```





```
# account.views

from rest_framework import viewsets
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import CombinedUserPersonSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class CombinedUserProfileViewSet(RetrieveModelMixin, UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = CombinedUserPersonSerializer
    
    def get_queryset(self):
        return User.objects.all()

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(user, data=request.data, partial=request.method == 'PATCH')
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
```

about the `me` action👆: this funtion returns the profile associated with the user model. therefore, the url `<site-address>/account/persons/me` returns the user's profile in a rest response.



```
# account.urls

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CombinedUserProfileViewSet

router = DefaultRouter()
router.register(r'persons', CombinedUserProfileViewSet, basename='user')

urlpatterns = [
    path(r'', include(router.urls)),
]
```









**map:** both the profile and user models and their configurations are implemented; but they are not connected together. the next part (signals) takes care of that so when a user model is created, a profile model associated to it is automatically created. (this means that the `Person` and `User` models had to be connected manually before)

## connecting the `User` and `Person` models

in the `account` app, write in the `signals` file:

```
# account.signals

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Person
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_person(sender, instance, created, **kwargs):
    if created:
        Person.objects.create(user=instance)
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_person(sender, instance, **kwargs):
    instance.person.save()
```

to get this `signal` run automatically, get it in the ready state:

```
# account.apps

from django.apps import AppConfig


class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'

    def ready(self) -> None:
        import account.signals
```











**map:** now, the url `account/persons/me` containing the proper access token in the request header will return the `core.User` and `account.Person` all together. 

**note:** the email field in the `account.serializers` is not `read_only`, as some users may decide to change their emails. you can change it there.


congrats! you got yourself a jwt auth django project!










<br></br>
<br></br>
<br></br>
<br></br>
<br></br>
<br></br>
<br></br>
<br></br>
<br></br>

a big thanks to the AIs that helped me in this project;

perplexity.ai

blackbox.ai

and

chatgpt.com , copilot.microsoft.com (not quite a lot)

<br></br>
<br></br>



this markdown text was created on https://markdownlivepreview.com/