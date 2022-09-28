from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class ContainsUppercaseValidator:
    def __init__(self):
        pass

    def validate(self, password, user=None):
        if not any(p.isUpper() for p in password):
            raise ValidationError(
                _("This password must contain at least 1 uppercase character."),
                code='password_no_upper',
           
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 uppercase character."
        )



class ContainsLowercaseValidator:
    def __init__(self):
        pass

    def validate(self, password, user=None):
        if not any(p.isLower() for p in password):
            raise ValidationError(
                _("This password must contain at least 1 lowercase character."),
                code='password_no_lower',
           
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 lowercase character."
        )



class ContainsSpecialValidator:
    def __init__(self):
        pass

    def validate(self, password, user=None):
        if not any(not p.isalnum() for p in password):
            raise ValidationError(
                _("This password must contain at least 1 special character."),
                code='password_no_special',
           
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 special character."
        )

class ContainsNumberValidator:
    def __init__(self):
        pass

    def validate(self, password, user=None):
        if not any(not p.isdigit() for p in password):
            raise ValidationError(
                _("This password must contain at least 1 number."),
                code='password_no_number',
           
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 1 number."
        )