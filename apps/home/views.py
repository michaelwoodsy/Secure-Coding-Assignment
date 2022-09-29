import logging, os

from cryptography.fernet import Fernet

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from apps.home.forms import ProjectForm, UserProfileForm
from apps.home.models import Project, UserProfile

logger = logging.getLogger(__name__)


##
## Projects
##
@login_required(login_url="login/")
def index(request):
    context = {"segment": "index"}
    logger.info("GET index page (all projects)")
    projects = Project.objects.all()
    return render(
        request,
        "home/index.html",
        {"context": context, "projects": projects, "number_of_projects": len(projects)},
    )


@login_required(login_url="login/")
def view_project(request, project_id):
    context = {"segment": "index"}
    logger.info("GET project page for project %s", project_id)
    project = get_object_or_404(Project, pk=project_id)
    return render(
        request,
        "home/view_project.html",
        {"context": context, "project": project, "user": request.user},
    )


@login_required(login_url="login/")
def new_project(request):
    context = {"segment": "index"}
    msg = None
    if request.method == "POST":
        logger.info("POST new project")
        project_form = ProjectForm(data=request.POST, files=request.FILES)
        if project_form.is_valid():
            project = project_form.save(commit=False)
            project.completion = 0
            project.save()
            for member in project_form.cleaned_data["members"]:
                project.members.add(member.id)
            return redirect(reverse("index"))

        else:
            msg = "Error/s in form"

    else:
        logger.info("GET new project")
        project_form = ProjectForm()

    return render(
        request,
        "home/edit_project.html",
        {
            "context": context,
            "form": project_form,
            "msg": msg,
            "new_or_edit": "new",
        },
    )


@login_required(login_url="login/")
def edit_project(request, project_id, user_id):
    if request.user.id != user_id:
        return render(request, "home/page-403.html", {"msg": "cannot edit this project"})

    context = {"segment": "index"}
    msg = None
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        logger.info("POST edit project %s", project.name)
        project_form = ProjectForm(data=request.POST, files=request.FILES, instance=project)

        if project_form.is_valid():
            project = project_form.save()
            msg = "Project saved"

        else:
            msg = "Error/s in form"

    else:
        logger.info("GET edit project")
        user = get_object_or_404(UserProfile, user_id=user_id)
        if user not in project.members.all():
            return render(request, "home/page-403.html", {"msg": "user does not belong to project"})

    project_form = ProjectForm(instance=project)
    return render(
        request,
        "home/edit_project.html",
        {"context": context, "form": project_form, "msg": msg, "new_or_edit": "edit"},
    )


##
## Profiles
##
@login_required(login_url="login/")
def view_profile(request, user_id):
    context = {"segment": "profiles"}
    logger.info("GET profile for %s", user_id)
    profile = UserProfile.objects.filter(user=user_id).first()
    return render(request, "home/view_profile.html", {"context": context, "profile": profile})


@login_required(login_url="login/")
def edit_profile(request, user_id):
    if request.user.id != user_id:
        return render(request, "home/page-403.html", {"msg": "cannot edit this user"})

    context = {"segment": "my_profile"}
    logger.info("GET/POST (edit) profile for %s", user_id)
    profile = get_object_or_404(UserProfile, pk=user_id)
    msg = None

    if request.method == "POST":
        logger.info("POST edit profile for %s", user_id)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if profile_form.is_valid():
            # False means that we need to clear the file
            if profile_form.cleaned_data["picture_file"] == False:
                os.remove(profile.picture_file.path)
                profile.picture_file = None

            # None means no file passed
            elif profile_form.cleaned_data["picture_file"] is not None:
                profile.picture_file = profile_form.cleaned_data["picture_file"]

            # Update bio
            profile.bio = profile_form.cleaned_data["bio"]

            profile.save()
            msg = "Profile saved"
            logger.info("saved new profile data for user %s", profile.user.username)

        else:
            # early return to fix form
            return render(
                request,
                "home/edit_profile.html",
                {"context": context, "form": profile_form, "user": profile.user, "msg": "Error/s in form"},
            )

    # need to (re)load content of profile into form (same for GET and POST)
    profile = UserProfile.objects.filter(user_id=user_id).first()
    profile_form = UserProfileForm(instance=profile)
    if profile and profile.bio:
        profile_form.fields["bio"].initial = profile.bio

    return render(
        request,
        "home/edit_profile.html",
        {"context": context, "form": profile_form, "user": profile.user, "msg": msg},
    )


@login_required(login_url="login/")
def all_profiles(request):
    context = {"segment": "profiles"}
    logger.info("GET all profiles")
    all_profiles = UserProfile.objects.all()
    return render(request, "home/all_profiles.html", {"context": context, "profiles": all_profiles})


##
## admin
##
@login_required(login_url="login/")
def django_admin(request):
    return HttpResponseRedirect(reverse("admin:index"))


@login_required(login_url="login/")
def debug(request):
    if (
            "Referer" in request.headers and
            request.headers["Referer"] == settings.TRUSTED_REFERER and
            request.user.is_superuser
    ):
        with open(os.path.join(settings.LOGGING_PATH, settings.LOGFILE), "r") as f:
            content = f.read()
        response = HttpResponse(content, "text/plain")
        return response

    return render(request, "home/page-403.html", {"msg": "wrong referer in request"})


@login_required(login_url="login/")
def billing(request):
    if (
            request.user.is_superuser
    ):
        return render(request, "home/billing.html")

    return render(request, "home/page-403.html", {"msg": "only superuser can see this"})
