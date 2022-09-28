import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError

##
## Helper functions
##

# Overwrite existing files for bio files
# adapted from https://gist.github.com/fabiomontefuscolo/1584462
class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


##
## Model classes
##

def check_file_size(file):
  filesize = file.size

  if filesize > 3145728:
    raise ValidationError("You cannot upload an image larger than 3MB")
  else :
    return file


def validate_file_extension(value):
    if value.file.content_type != 'application/pdf':
        raise ValidationError(u'Error message')

class ExtensionValidator(RegexValidator):
    def __init__(self, extensions, message=None):
        if not hasattr(extensions, '__iter__'):
            extensions = [extensions]
        regex = '\.(%s)$' % '|'.join(extensions)
        if message is None:
            message = 'File type not supported. Accepted types are: %s.' % ', '.join(extensions)
        super(ExtensionValidator, self).__init__(regex, message)

    def __call__(self, value):
        super(ExtensionValidator, self).__call__(value.name)

class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.CharField(max_length=100, blank=True, null=True)
    picture_file = models.FileField(upload_to="profile_pics", blank=True, null=True, validators=[ExtensionValidator(['png', 'jpg', 'jpeg']), check_file_size])

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    picture_file = models.FileField(upload_to="project_pics", blank=True, null=True, validators=[ExtensionValidator(['png', 'jpg', 'jpeg']), check_file_size])
    budget = models.FloatField(validators=[MinValueValidator(0)])
    completion = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    members = models.ManyToManyField(UserProfile)

    def __str__(self):
        return self.name
