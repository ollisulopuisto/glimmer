# SPDX-License-Identifier: GPL-3.0-only
# SPDX-FileCopyrightText: 2026 ugfugl.io

"""Every embedded executable must be launchable on the app's minimum macOS."""

from pathlib import Path
import plistlib
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]


class DeploymentTargetTests(unittest.TestCase):
    def app_minimum(self):
        with (ROOT / "Glimmer/Info.plist").open("rb") as stream:
            return plistlib.load(stream)["LSMinimumSystemVersion"]

    def test_embedded_helpers_match_the_app_minimum(self):
        for path in ("LoginHelper/Info.plist", "helper/Info.plist"):
            with self.subTest(path=path), (ROOT / path).open("rb") as stream:
                self.assertEqual(plistlib.load(stream)["LSMinimumSystemVersion"], self.app_minimum())

    def test_compiler_targets_match_bundle_metadata(self):
        project = (ROOT / "Glimmer.xcodeproj/project.pbxproj").read_text()
        targets = re.findall(r"MACOSX_DEPLOYMENT_TARGET = ([\d.]+);", project)
        self.assertTrue(targets)
        self.assertEqual(set(targets), {self.app_minimum()})
        makefile = (ROOT / "Makefile").read_text()
        helper = re.search(r"^HELPER_TARGET\s*:=\s*arm64-apple-macos([\d.]+)$", makefile, re.MULTILINE)
        self.assertIsNotNone(helper)
        self.assertEqual(helper.group(1), self.app_minimum())
