from base64 import urlsafe_b64encode
import logging

from cryptography.fernet import Fernet

from django.conf import settings
from django.core import mail, validators, serializers
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes

from django.contrib.auth.forms import PasswordResetForm



from apps.home.models import UserProfile

from .forms import LoginForm, SignUpForm

logger = logging.getLogger(__name__)


def login_user(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                response = HttpResponseRedirect("/")
                response.set_cookie(
                    "superuser", Fernet(settings.FERNET).encrypt(str(user.is_superuser).encode()).decode()
                )
                return response
            else:
                msg = "Invalid credentials"

        else:
            msg = "Error in form"

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)

        if user_does_not_exist(form) and form.is_valid():
            user = form.save()
            UserProfile(user_id=user.id).save()
            send_confirmation_email(form.cleaned_data["email"])
            success = True
            msg = "User created successfully"

        else:
            msg = "Error/s in form"

    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


def reset_password(request):
    msg = None
    success = False

    if request.method == "POST":
        form = PasswordResetForm(request.POST)

        if form.is_valid():
          data = form.cleaned_data.get("email")
          user_from_email = User.objects.get(email=data)
          if user_from_email is not None:
            token = default_token_generator.make_token(user_from_email)
            send_reset_password_email(user_from_email, request, token)
              
          return render(request, "accounts/password_reset_done.html")
        else:
            msg = "Error/s in form"

    else:
        form = PasswordResetForm()

    return render(request, "accounts/password_reset.html", {"form": form, "msg": msg, "success": success})


def send_reset_password_email(user: User, request, token):
  connection = mail.get_connection()
  connection.open
  subject = "Password Reset Requested"
  email_template_name = "accounts/password_reset_email.txt"
  host = request.get_host()
  email_json = {
  "email": user.email,
  'domain': host,
  'site_name': 'Website',
  "uid": urlsafe_base64_encode(force_bytes(user.id)),
  "user": user,
  'token': token,
  'protocol': 'http',
  }
  email = render_to_string(email_template_name, email_json)
  to_send = mail.EmailMessage(
      subject,
      email,
      "seng402@unsecure.app",
      [user.email],
      connection=connection,
  )
  to_send.send()
  connection.close()

##
# Helper functions
##



def user_does_not_exist(form):
    rawsql = "select * from auth_user where email like %s"
    result = User.objects.raw(rawsql, [form.data["email"]])
    if len(result) > 0:
        form.add_error("email", "email taken")

    return len(result) == 0


def email_is_valid(form):
    result = False
    try:
        validators.validate_email(form.data["email"])
        result = True
    except ValidationError as e:
        form.add_error("email", "email is invalid")
    return result


def send_confirmation_email(email):
    connection = mail.get_connection()
    connection.open
    to_send = mail.EmailMessage(
        "Welcome to SENG402 Unsecure App",
        "You'll enjoy playing around with all my flaws.",
        "seng402@unsecure.app",
        [email],
        connection=connection,
    )
    to_send.send()
    connection.close()



