from django.contrib.auth.models import User, Group, Permission
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.get(pk=2)
        group, created = Group.objects.get_or_create(
            name='profile_manager',
        )
        permission_profile = Permission.objects.get(
            codename='view_profile',
        )
        permission_logentry = Permission.objects.get(
            codename='view_permission'
        )

        #Добавить разрешение в группу
        group.permissions.add(permission_profile)

        #Добавить пользователя в группу
        user.groups.add(group)

        #связать пользователя с разрешением напрямую
        user.user_permissions.add(permission_logentry)

        user.save()
        group.save()

