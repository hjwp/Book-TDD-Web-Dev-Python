import unittest
from sourcetree import (
    SourceTree,
)


class RequirementTestCase(unittest.TestCase):
    def test_en_GB_locale_is_installed(self):
        sourcetree = SourceTree()

        locales = sourcetree.run_command("locale -a").split("\n")
        # debian  sudo locale-gen en_GB.UTF-8 && sudo update-locale
        # arch : https://wiki.archlinux.org/title/locale
        # uncomment en_GB.UTF-8

        # cd /etc && sudo git diff  3 i have etckeeper installed
        """
        diff --git a/locale.gen b/locale.gen
        index 2f21f03..210ee98 100644
        --- a/locale.gen
        +++ b/locale.gen
        @@ -157,7 +157,7 @@
         #en_CA ISO-8859-1
         #en_DK.UTF-8 UTF-8
         #en_DK ISO-8859-1
        -#en_GB.UTF-8 UTF-8
        +en_GB.UTF-8 UTF-8
         #en_GB ISO-8859-1
         #en_HK.UTF-8 UTF-8
         #en_HK ISO-8859-1
        """

        assert (
            "en_GB.utf8" in locales,
            "Lacking en_GB locale. " "This interferes with checks for output.",
        )
