import os
from os.path import join, exists
from multiprocessing import cpu_count
from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint, info
from pythonforandroid.util import current_directory
import sh

class LibffiRecipe(Recipe):
    name = 'libffi'
    version = '3.4.4'
    url = 'https://github.com/libffi/libffi/releases/download/v{version}/libffi-{version}.tar.gz'

    # This recipe is self-contained and does not need to declare patches.

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        build_dir = self.get_build_dir(arch.arch)
        install_prefix = self.ctx.get_python_install_dir(arch.arch)
        info(f"[{self.name}] Installation prefix for {arch.arch} will be: {install_prefix}")

        with current_directory(build_dir):
            m4_dir = join(build_dir, 'm4')
            if not exists(m4_dir):
                os.makedirs(m4_dir)
            
            # --- THIS IS THE FINAL, CORRECTED PATH ---
            # self.get_recipe_dir() is always relative to the current recipe,
            # so we navigate from there to the project's m4 directory.
            recipe_dir = self.get_recipe_dir()
            project_m4_file = join(recipe_dir, '..', '..', 'm4', 'lt_sys_symbol_uscore.m4')
            # --- END OF FIX ---

            if not exists(project_m4_file):
                raise IOError(f"M4 macro file not found at {project_m4_file}")

            sh.cp("-f", project_m4_file, m4_dir)
            info(f"Copied m4 macro for {arch.arch} from {project_m4_file}")

            shprint(sh.Command('autoreconf'), '-vif', _env=env)

            configure_cmd = sh.Command('./configure')
            shprint(configure_cmd,
                    '--host=' + arch.command_prefix,
                    '--prefix=' + install_prefix,
                    '--enable-shared',
                    '--disable-static',
                    _env=env)

            shprint(sh.make, f'-j{cpu_count()}', _env=env)
            shprint(sh.make, 'install', _env=env)

    def get_include_dirs(self, arch):
        return [join(self.ctx.get_python_install_dir(arch.arch), 'include')]

    def get_lib_dirs(self, arch):
        return [join(self.ctx.get_python_install_dir(arch.arch), 'lib')]

recipe = LibffiRecipe()