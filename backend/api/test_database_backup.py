from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, override_settings


@override_settings(DATABASES={'default': {
    'ENGINE': 'django.db.backends.postgresql', 'NAME': 'backup_test',
    'USER': 'backup_user', 'PASSWORD': 'private-test-password',
    'HOST': '127.0.0.1', 'PORT': '5432',
}})
class DatabaseBackupTests(SimpleTestCase):
    @patch('api.management.commands.backup_database.subprocess.run')
    def test_uses_django_connection_and_keeps_password_out_of_arguments(self, run):
        def dump(command, **kwargs):
            kwargs['stdout'].write(b'test dump')
        run.side_effect = dump
        with TemporaryDirectory() as directory:
            output = Path(directory) / 'database.dump'
            call_command('backup_database', str(output), verbosity=0)
            self.assertEqual(output.read_bytes(), b'test dump')
        command = run.call_args.args[0]
        self.assertEqual(command[command.index('--host') + 1], '127.0.0.1')
        self.assertEqual(command[command.index('--port') + 1], '5432')
        self.assertEqual(command[command.index('--dbname') + 1], 'backup_test')
        self.assertNotIn('private-test-password', command)
        self.assertEqual(run.call_args.kwargs['env']['PGPASSWORD'], 'private-test-password')
        self.assertTrue(run.call_args.kwargs['check'])

    @patch('api.management.commands.backup_database.subprocess.run')
    def test_existing_backup_is_not_overwritten(self, run):
        with TemporaryDirectory() as directory:
            output = Path(directory) / 'database.dump'
            output.write_bytes(b'existing backup')
            with self.assertRaises(CommandError):
                call_command('backup_database', str(output))
            self.assertEqual(output.read_bytes(), b'existing backup')
        run.assert_not_called()

    @patch('api.management.commands.backup_database.subprocess.run', side_effect=subprocess.CalledProcessError(1, ['pg_dump']))
    def test_failed_dump_is_removed_and_deployment_can_stop(self, run):
        with TemporaryDirectory() as directory:
            output = Path(directory) / 'database.dump'
            with self.assertRaises(CommandError):
                call_command('backup_database', str(output))
            self.assertFalse(output.exists())
