from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--username', dest='username')
        parser.add_argument('--password', dest='password')

    def handle(self, *args, **options):
        User = get_user_model()

        username = options.get('username') or input('Username: ').strip()
        if not username:
            raise CommandError('Username is required.')

        password = options.get('password')
        if password is None:
            password = input('Password: ')
            password2 = input('Password again: ')
            if password != password2:
                raise CommandError('Passwords do not match.')

        email = ''

        if User.objects.filter(username=username).exists():
            raise CommandError('User with this username already exists.')

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created.'))
