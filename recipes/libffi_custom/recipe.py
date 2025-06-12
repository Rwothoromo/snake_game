from pythonforandroid.recipes.libffi import LibFFIRecipe as OriginalLibFFIRecipe
from pythonforandroid.logger import info
import os
import sh

class CustomLibFFIRecipe(OriginalLibFFIRecipe):
    # This recipe overrides the 'libffi' recipe
    name = 'libffi'
    
    # We explicitly define the patches list, pointing to our local copies
    patches = ['remove-version-info.patch']

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        
        info('Custom libffi recipe: Copying m4 macro file...')
        build_dir = self.get_build_dir(arch.arch)
        m4_dir = os.path.join(build_dir, 'm4')
        if not os.path.exists(m4_dir):
            os.makedirs(m4_dir)
        
        recipe_dir = self.get_recipe_dir()
        project_m4_file = os.path.join(recipe_dir, '..', '..', 'm4', 'lt_sys_symbol_uscore.m4')
        
        sh.cp("-f", project_m4_file, m4_dir)
        info("Successfully copied m4 macro file for libffi.")

recipe = CustomLibFFIRecipe()