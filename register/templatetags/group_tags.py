from django import template
from django.contrib.auth.models import Group

# Declares a variable for storing the template library
register = template.Library()


@register.filter(name="is_admin")
def is_admin(user):
    try:
        group = Group.objects.get(name='AdminGroup')
    except Group.DoesNotExist:
        return False
    return group in user.groups.all()
