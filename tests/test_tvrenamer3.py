import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import tvrenamer3


class PatternAndFilenameTests(unittest.TestCase):
    def test_extracts_common_episode_formats(self):
        cases = {
            'Show.S01E02.mkv': (1, 2),
            'Show.S01.E02.mkv': (1, 2),
            'Show.1x03.mkv': (1, 3),
            'Show.Season.2.Episode.04.mkv': (2, 4),
        }
        for filename, expected in cases.items():
            with self.subTest(filename=filename):
                self.assertEqual(
                    tvrenamer3.PatternUtils.extract_season_episode(filename), expected
                )

    def test_skips_multi_episode_names(self):
        self.assertEqual(
            tvrenamer3.PatternUtils.extract_season_episode('Show.S01E01-E02.mkv'),
            (None, None)
        )

    def test_clean_filename_handles_reserved_names_and_empty_values(self):
        self.assertEqual(tvrenamer3.FileUtils.clean_filename('CON'), '_CON')
        self.assertEqual(tvrenamer3.FileUtils.clean_filename('bad<name>'), 'badname')
        self.assertEqual(tvrenamer3.FileUtils.clean_filename(''), 'Unknown')


class RenameSafetyTests(unittest.TestCase):
    def test_preflight_detects_duplicate_destinations(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            first = root / 'first.mkv'
            second = root / 'second.mkv'
            first.touch()
            second.touch()
            operations = [
                tvrenamer3.RenameOperation(first, 'same.mkv'),
                tvrenamer3.RenameOperation(second, 'same.mkv'),
            ]
            errors = tvrenamer3.TVSeriesRenamer._preflight_renames(operations)
            self.assertTrue(any('destinazione duplicata' in error for error in errors))

    def test_restore_manifest_keeps_recursive_paths(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            season = root / 'Season 1'
            season.mkdir()
            original = season / 'Show.S01E01.mkv'
            renamed = season / 'Show - S01E01 - Pilot.mkv'
            original.touch()

            manager = tvrenamer3.RestoreScriptManager(root, tvrenamer3.TextManager(tvrenamer3.Language.ITALIAN))
            manager.add_rename(original, renamed)
            script_name = manager.create_script()
            self.assertIsNotNone(script_name)
            manifest = root / manager.manifest_name
            data = json.loads(manifest.read_text(encoding='utf-8'))
            self.assertEqual(data['renames'][0]['old'], 'Season 1/Show.S01E01.mkv')
            self.assertEqual(data['renames'][0]['new'], 'Season 1/Show - S01E01 - Pilot.mkv')
            compile((root / script_name).read_text(encoding='utf-8'), script_name, 'exec')

            original.rename(renamed)
            result = subprocess.run(
                [sys.executable, str(root / script_name)],
                input='s\n', text=True, capture_output=True, cwd=str(root)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(original.exists())
            self.assertFalse(renamed.exists())
            self.assertFalse((root / script_name).exists())


if __name__ == '__main__':
    unittest.main()
