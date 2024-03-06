from django import template
from django.contrib.auth.models import Group

# Declares a variable for storing the template library
register = template.Library()


# Registers the is_admin filter
@register.filter(name="is_admin")
# Defines the is_admin filter
def is_admin(user):
    """
    Checks if the user is in the AdminGroup
    :param user:
    :return:
    """
    # Tries to get the AdminGroup
    try:
        group = Group.objects.get(name='AdminGroup')
    # If the AdminGroup does not exist, returns False
    except Group.DoesNotExist:
        return False
    # Returns True if the user is in the AdminGroup, False otherwise
    return group in user.groups.all()
