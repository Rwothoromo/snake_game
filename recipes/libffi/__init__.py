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

    @property
    def built_libraries(self):
        """
        Dynamically finds the .so file in the correct, arch-specific subdirectory.
        This is a workaround for the complex build process of libffi.
        """
        first_arch = self.ctx.archs[0]
        host_string = self.get_host(first_arch)
        # The key fix is here: do NOT include self.name in the path, as the
        # build system adds it automatically.
        libs_path = join(host_string, '.libs')
        return {'libffi.so': libs_path}

    def get_host(self, arch):
        """Returns the host string for a given architecture object."""
        if 'arm64' in arch.arch:
            return 'aarch64-unknown-linux-android'
        elif 'armeabi-v7a' in arch.arch:
            return 'arm-unknown-linux-androideabi'
        raise ValueError(f"Unsupported architecture: {arch.arch}")

    def get_build_container_dir(self, arch_iface):
        """
        Overridden to point to the correct subdirectory where libffi builds,
        which is named after the host platform string.
        """
        arch_name = arch_iface.arch if hasattr(arch_iface, 'arch') else arch_iface
        return join(self.ctx.build_dir, 'other_builds', self.name, arch_name, self.name)

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        build_dir = self.get_build_dir(arch.arch)
        install_prefix = self.ctx.get_python_install_dir(arch.arch)
        info(f"[{self.name}] Installation prefix will be: {install_prefix}")

        with current_directory(build_dir):
            m4_dir = join(build_dir, 'm4')
            if not exists(m4_dir):
                os.makedirs(m4_dir)
            
            this_recipe_dir = os.path.dirname(__file__)
            project_m4_file = join(this_recipe_dir, '..', '..', 'm4', 'lt_sys_symbol_uscore.m4')
            sh.cp("-f", project_m4_file, join(m4_dir, 'lt_sys_symbol_uscore.m4'))

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