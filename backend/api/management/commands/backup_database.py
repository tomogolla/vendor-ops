"""Create a PostgreSQL backup using the same connection settings as Django."""
import os
from pathlib import Path
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Create a custom-format PostgreSQL backup (restore with pg_restore).'

    def add_arguments(self, parser):
        parser.add_argument('output', help='Destination .dump file; existing files are never overwritten.')

    def handle(self, *args, **options):
        database = settings.DATABASES['default']
        if database['ENGINE'] != 'django.db.backends.postgresql':
            raise CommandError('This command requires PostgreSQL.')
        output = Path(options['output']).resolve()
        env = os.environ.copy()
        env['PGPASSWORD'] = str(database.get('PASSWORD') or '')
        command = [
            'pg_dump', '--no-password', '--format=custom',
            '--host', str(database.get('HOST') or '127.0.0.1'),
            '--port', str(database.get('PORT') or '5432'),
            '--username', str(database['USER']), '--dbname', str(database['NAME']),
        ]
        try:
            # Exclusive creation avoids overwriting earlier backups; mode 0600 keeps data private.
            descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except OSError as exc:
            raise CommandError(f'Cannot create backup destination: {exc}') from exc
        try:
            with os.fdopen(descriptor, 'wb') as backup:
                subprocess.run(command, env=env, stdout=backup, check=True)
        except (OSError, subprocess.CalledProcessError) as exc:
            output.unlink(missing_ok=True)
            raise CommandError('PostgreSQL backup failed. Check pg_dump installation, connection and permissions.') from exc
        self.stdout.write(self.style.SUCCESS(f'PostgreSQL backup created: {output}'))
