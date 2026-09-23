import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group
from core.roles import setup_roles, ROLE_CEO, ROLE_CASHIER, ROLE_GRAPHICS, ROLE_LOGISTICS

# Ensure role groups exist
setup_roles()
print("Initialized RBAC Groups: CEO, Cashier, Graphics, Logistics.")

# Setup Superuser (admin)
username = 'admin'
email = 'admin@desaintstationeries.com'
password = 'desaintadmin2026'

admin_user, created = User.objects.get_or_create(username=username, defaults={'email': email})
admin_user.is_staff = True
admin_user.is_superuser = True
admin_user.email = email
admin_user.set_password(password)
admin_user.save()

ceo_group = Group.objects.get(name=ROLE_CEO)
admin_user.groups.add(ceo_group)
print(f"Superuser '{username}' configured with CEO role.")

# Setup demo staff accounts for testing each role
demo_users = [
    ('solomon', 'solomon@desaintstationeries.com', 'solomon2026', ROLE_CEO, 'Solomon', 'Naito'),
    ('cashier_sunyani', 'cashier@desaintstationeries.com', 'cashier2026', ROLE_CASHIER, 'Ama', 'Osei'),
    ('graphics_lead', 'graphics@desaintstationeries.com', 'graphics2026', ROLE_GRAPHICS, 'Kofi', 'Mensah'),
    ('dispatch_officer', 'logistics@desaintstationeries.com', 'logistics2026', ROLE_LOGISTICS, 'Kwaku', 'Boateng'),
]

for u_name, u_email, u_pwd, u_role, first_name, last_name in demo_users:
    u, created = User.objects.get_or_create(
        username=u_name,
        defaults={'email': u_email, 'first_name': first_name, 'last_name': last_name}
    )
    u.is_staff = True
    u.is_superuser = False
    u.set_password(u_pwd)
    u.save()
    group = Group.objects.get(name=u_role)
    u.groups.clear()
    u.groups.add(group)
    status = "Created" if created else "Updated"
    print(f"{status} demo staff '{u_name}' with role '{u_role}' (password: {u_pwd}).")

