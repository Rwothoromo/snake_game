import os
from os.path import join, exists
from multiprocessing import cpu_count
from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint, info, warning
from pythonforandroid.util import current_directory
import sh

class LibFFIRecipe(Recipe):
    name = 'libffi'
    version = '3.4.4'
    url = 'https://github.com/libffi/libffi/releases/download/v{version}/libffi-{version}.tar.gz'

    def should_build(self, arch):
        # We need to build every time to ensure our custom M4 copy happens
        return True

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        build_dir = self.get_build_dir(arch.arch)
        install_prefix = self.ctx.get_python_install_dir(arch.arch)
        info(f"[{self.name}] Installation prefix will be: {install_prefix}")

        with current_directory(build_dir):
            # THIS IS THE CRITICAL FIX:
            # We ensure the M4 file is in place before any build commands are run.
            m4_dir = join(build_dir, 'm4')
            if not exists(m4_dir):
                os.makedirs(m4_dir)
            
            project_root = os.getcwd()
            # This path is relative to the *buildozer execution directory*, which is the project root.
            project_m4_file = join(project_root, 'm4', 'lt_sys_symbol_uscore.m4')
            
            # Ensure the source file exists before copying
            if not exists(project_m4_file):
                raise IOError(f"M4 macro file not found at {project_m4_file}")

            sh.cp("-f", project_m4_file, join(m4_dir, 'lt_sys_symbol_uscore.m4'))
            info(f"Copied {project_m4_file} to {m4_dir}")
            # END OF CRITICAL FIX

            # Now, we run the standard build commands for libffi.
            shprint(sh.Command('autoreconf'), '-vif', _env=env)

            sysroot_path = join(self.ctx.ndk.llvm_prebuilt_dir, 'sysroot')
            configure_cmd = sh.Command('./configure')
            shprint(configure_cmd,
                    '--host=' + arch.command_prefix,
                    '--prefix=' + install_prefix,
                    '--enable-shared',
                    '--disable-static',
                    '--with-sysroot=' + sysroot_path,
                    _env=env)

            jobs = cpu_count()
            shprint(sh.make, f'-j{jobs}', _env=env)
            shprint(sh.make, 'install', _env=env)

    def get_include_dirs(self, arch):
        install_dir = self.ctx.get_python_install_dir(arch.arch)
        return [join(install_dir, 'include')]

    def get_lib_dirs(self, arch):
        install_dir = self.ctx.get_python_install_dir(arch.arch)
        return [join(install_dir, 'lib')]
        
recipe = LibFFIRecipe()