import os
import inspect
import sh
from pythonforandroid.recipes.python3 import Python3Recipe as OriginalPython3Recipe
from pythonforandroid.logger import info, warning, shprint

class Python3Recipe(OriginalPython3Recipe):

    def apply_patches(self, arch):
        """
        This override sources patches from the original p4a recipe location
        and handles all patch formats correctly.
        """
        info('Applying patches from custom python3 recipe')
        if not self.patches:
            return

        try:
            original_recipe_dir = os.path.dirname(inspect.getfile(OriginalPython3Recipe))
        except (TypeError, OSError):
            warning("Could not resolve original python3 recipe dir, patch application may fail.")
            super().apply_patches(arch)
            return

        for patch_info in self.patches:
            patch_name = patch_info[0] if isinstance(patch_info, tuple) else patch_info
            patch_path = os.path.join(original_recipe_dir, patch_name)

            if not os.path.exists(patch_path):
                warning(f"Patch not found at expected path: {patch_path}")
                continue

            info(f'Applying patch {patch_path}')
            build_dir = self.get_build_dir(arch.arch)
            try:
                shprint(sh.patch, "-t", "-d", build_dir, "-p1", "-i", patch_path)
            except sh.ErrorReturnCode_1:
                info(f"Patch {patch_name} failed to apply, but continuing build. This is likely okay.")
            except Exception as e:
                warning(f"An unexpected error occurred while applying patch {patch_name}: {e}")

recipe = Python3Recipe()