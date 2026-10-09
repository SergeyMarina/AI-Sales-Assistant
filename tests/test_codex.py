import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import configuration
import drafts
import verify
import write_letter


class ConfigurationTests(unittest.TestCase):
    def test_all_steps_use_same_config_outside_project(self):
        with tempfile.TemporaryDirectory() as folder:
            previous = os.getcwd()
            try:
                os.chdir(folder)
                with patch.dict(os.environ, {}, clear=True):
                    expected = str(ROOT / 'config.json')
                    for module in (configuration, verify, drafts, write_letter):
                        self.assertEqual(module.find_config(), expected)
            finally:
                os.chdir(previous)

    def test_explicit_and_environment_paths_do_not_fall_back(self):
        with patch.dict(os.environ, {'AIOP_CONFIG': '/tmp/sales-custom.json'}):
            for module in (configuration, verify, drafts, write_letter):
                self.assertEqual(module.find_config(), str(Path('/tmp/sales-custom.json').resolve()))
            self.assertEqual(verify.find_config('/tmp/sales-missing.json'), str(Path('/tmp/sales-missing.json').resolve()))

    def test_summary_does_not_expose_mail_or_signature(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'config.json'
            path.write_text(json.dumps({'pochta': {'parol': 'secret-sentinel'},
                                        'pisma': {'podpis': 'private-signature'},
                                        'portret_klienta': {'region': '16'}}))
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/configuration.py'),
                                     '--config', str(path), '--summary'], capture_output=True, text=True, check=True)
            self.assertNotIn('secret-sentinel', result.stdout)
            self.assertNotIn('private-signature', result.stdout)
            self.assertEqual(json.loads(result.stdout)['portret_klienta']['region'], '16')


class InstallerTests(unittest.TestCase):
    def test_install_preserves_custom_profile_and_stays_local(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder) / 'project with spaces'
            shutil.copytree(ROOT, project, ignore=shutil.ignore_patterns('.git', 'config.json', '__pycache__', 'out', 'data'))
            fake_home = Path(folder) / 'home'
            fake_home.mkdir()
            env = dict(os.environ, HOME=str(fake_home), PRODAZHI_PYTHON=sys.executable)
            command = ['bash', str(project / 'install.sh')]
            subprocess.run(command, cwd=folder, env=env, check=True, capture_output=True)
            config_path = project / 'config.json'
            config = json.loads(config_path.read_text())
            self.assertEqual(config['pochta']['parol'], '')
            self.assertIsNone(config['istochniki']['rmsp_dt_category'])
            self.assertEqual(config_path.stat().st_mode & 0o777, 0o600)
            config['portret_klienta']['region'] = '61'
            config['pochta']['parol'] = 'preserve-me'
            config_path.write_text(json.dumps(config))
            before = config_path.read_bytes()
            subprocess.run(command, cwd=folder, env=env, check=True, capture_output=True)
            self.assertEqual(config_path.read_bytes(), before)
            self.assertEqual(list(fake_home.iterdir()), [])

    def test_invalid_existing_config_fails_without_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder) / 'project'
            shutil.copytree(ROOT, project, ignore=shutil.ignore_patterns('.git', 'config.json', '__pycache__', 'out', 'data'))
            (project / 'config.json').write_text('{broken')
            result = subprocess.run(['bash', str(project / 'install.sh')],
                                    env=dict(os.environ, PRODAZHI_PYTHON=sys.executable), capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((project / 'config.json').read_text(), '{broken')


class SmokeTests(unittest.TestCase):
    def test_script_help_is_offline(self):
        for script in (ROOT / 'scripts').glob('*.py'):
            with self.subTest(script=script.name):
                subprocess.run([sys.executable, str(script), '--help'],
                               cwd=ROOT, check=True, capture_output=True, timeout=10)

    def test_five_demo_reports_are_created(self):
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run([sys.executable, str(ROOT / 'scripts/report.py'), '--demo', '--out', folder],
                           cwd=ROOT, check=True, capture_output=True)
            reports = list(Path(folder).glob('*.html'))
            self.assertEqual(len(reports), 5)
            for report in reports:
                self.assertIn('</html>', report.read_text().lower())


if __name__ == '__main__':
    unittest.main()
