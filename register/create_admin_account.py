def create_admin_group():
    from django.contrib.auth.models import Group, Permission, User
    """Function to create a custom admin group and assign all permissions to it."""
    # Create the admin group
    admin_group, created = Group.objects.get_or_create(name='AdminGroup')

    # Get or create permissions
    permissions = Permission.objects.all()

    # Add the permissions to the group
    admin_group.permissions.set(permissions)

    # If the group was created, print a message otherwise print a different message
    if created:
        print('Custom admin group created and permissions assigned.')
    else:
        print('Custom admin group already exists.')


def create_default_admin_user():
    from django.contrib.auth.models import Group, User
    from payapp.models import Account
    """Function to create an admin account as per specification."""
    # Check if the admin account already exists
    if not User.objects.filter(username='admin1').exists():
        # Create the admin account
        admin = User.objects.create_user('admin1', password='admin1', email="admin1@email.com")

        # Add the admin to the admin group
        admin_group = Group.objects.get(name='AdminGroup')
        admin.groups.add(admin_group)

        # Print a message to confirm the account was created
        print('Admin user created.')

        # Create an account for the admin user
        account = Account(user=admin)
        account.save()

    else:
        # Print a message to confirm the account already exists
        print('Admin account already exists.')


def create_admin_group_and_account(sender, **kwargs):
    """Function to create the admin group and account."""
    create_admin_group()
    create_default_admin_user()
    print('Admin group and account created successfully.')
