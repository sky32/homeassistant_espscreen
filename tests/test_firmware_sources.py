"""A board's configured origin drives Tessera, component and font URLs together (docs/PROFILES.md)."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'screen_manager/app'))
import core
import firmware_origins as sources
from firmware import Firmware, LenientLoader, profile_meta
from generate_entries import package_entry
import yaml


def load(text):
    return yaml.load(text, Loader=LenientLoader)


class FirmwareSources(unittest.TestCase):
    def tearDown(self):
        core.set_channel(None)
        core.set_version(None)

    def screen(self, board='ha-panel-s3'):
        return core.installation_yaml({'board': board, 'name': 'source-test', 'friendly_name': 'Source test'})

    def test_ha_panel_uses_same_fork_for_package_components_and_fonts(self):
        repository, branch = sources.source_for('ha-panel-s3')
        for channel in (None, 'main', 'dev'):
            with self.subTest(channel=channel):
                core.set_channel(channel)
                core.set_version('0.4.99')
                screen = load(self.screen())
                entry = load(package_entry('ha-panel-s3'))
                display = screen['packages']['display']
                self.assertEqual(display['url'], sources.repository_url(repository))
                self.assertEqual(display['ref'], branch)
                self.assertEqual(screen['substitutions']['GITHUB_REF'], branch)
                self.assertEqual(entry['substitutions']['GITHUB_REF'], branch)
                self.assertEqual(entry['external_components'][0]['source']['url'], display['url'] + '.git')
                self.assertEqual(entry['external_components'][0]['source']['ref'], '${GITHUB_REF}')
                self.assertEqual(entry['substitutions']['FONT_DIR'],
                                 f'https://raw.githubusercontent.com/{repository}/${{GITHUB_REF}}/fonts')

    def test_single_configuration_change_reaches_both_writers(self):
        with patch.dict(sources.BOARD_SOURCES, {'ha-panel-s3': ('example/firmware', 'main')}):
            screen = load(self.screen())
            entry = load(package_entry('ha-panel-s3'))
            self.assertEqual(screen['packages']['display']['url'], 'https://github.com/example/firmware')
            self.assertEqual(screen['packages']['display']['ref'], 'main')
            self.assertEqual(entry['external_components'][0]['source']['url'], 'https://github.com/example/firmware.git')
            self.assertEqual(entry['substitutions']['FONT_DIR'],
                             'https://raw.githubusercontent.com/example/firmware/${GITHUB_REF}/fonts')

    def test_official_board_keeps_channel_behavior(self):
        for channel, branch in ((None, 'main'), ('dev', 'dev'), ('main', 'screens-v0.4.99')):
            core.set_channel(channel)
            core.set_version('0.4.99')
            screen = load(self.screen('guition'))
            self.assertEqual(screen['packages']['display']['url'], core.REPO)
            self.assertEqual(screen['packages']['display']['ref'], branch)
            self.assertEqual(load(package_entry('guition'))['substitutions']['GITHUB_REF'], 'main')

    def test_configured_fork_profile_is_recognised(self):
        meta = profile_meta(self.screen())
        self.assertTrue(meta['screen'])
        self.assertEqual(meta['package'], 'packages/ha-panel-s3.yaml')
        repository, _ = sources.source_for('ha-panel-s3')
        self.assertTrue(sources.known_repository_url(sources.repository_url(repository) + '.git'))
        for url in (None, 'https://github.com/unknown/fork', core.REPO + '-other', core.REPO + '/evil'):
            self.assertFalse(sources.known_repository_url(url))

    def test_official_release_does_not_retarget_fork_even_on_main(self):
        for branch in ('feature/ha-panel-s3-chinese-locale', 'main'):
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'source-test.yaml'
                text = self.screen().replace('feature/ha-panel-s3-chinese-locale', branch)
                path.write_text(text)
                firmware = Firmware(tmp, tmp)
                self.assertFalse(firmware.set_branch(path.name, 'dev'))
                self.assertEqual(path.read_text(), text)


if __name__ == '__main__':
    unittest.main()
