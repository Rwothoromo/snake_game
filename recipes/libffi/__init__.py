# recipes/libffi/__init__.py
from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint, info, warning
from pythonforandroid.util import current_directory
import sh
import os
from os.path import join, exists
import re
from multiprocessing import cpu_count

class LibFFIRecipe(Recipe):
    """
    Custom python-for-android recipe for building libffi with Android cross-compilation,
    including patching for missing macros and ensuring proper build integration.
    """
    name = 'libffi'
    version = '3.4.4'
    url = 'https://github.com/libffi/libffi/releases/download/v{version}/libffi-{version}.tar.gz'
    built_libraries = {'libffi.so': 'lib'}

    def _get_arch_obj_and_name(self, arch_iface):
        """
        Given an arch interface (either an Arch object or a string), return the Arch object and its name.
        If only a string is provided and not found in self.ctx.archs, returns (None, arch_iface).
        """
        if hasattr(arch_iface, 'arch'):
            return arch_iface, arch_iface.arch
        else:
            for arch_obj in self.ctx.archs:
                if arch_obj.arch == arch_iface:
                    return arch_obj, arch_iface
            warning(f"[{self.name}] Could not find Arch object for arch string: {arch_iface}. Assuming it's a direct name.")
            return None, arch_iface

    def prebuild_arch(self, arch):
        """
        Optional prebuild step for the given architecture.
        Currently just calls the superclass implementation.
        """
        super().prebuild_arch(arch)

    def get_recipe_env(self, arch):
        """
        Returns the environment variables to use for building for the given architecture.
        Can be customized if needed.
        """
        env = super().get_recipe_env(arch)
        return env

    def build_arch(self, arch):
        """
        Main build step for libffi for the given architecture.
        - Copies the required m4 macro for LT_SYS_SYMBOL_USCORE.
        - Patches configure.ac to include m4_pattern_allow and AC_CONFIG_MACRO_DIRS.
        - Runs autoreconf to regenerate autotools files.
        - Configures, builds, and installs libffi into the Python install prefix for the arch.
        """
        env = self.get_recipe_env(arch)
        build_dir = self.get_build_dir(arch.arch)
        install_prefix = self.ctx.get_python_install_dir(arch.arch)
        info(f"[{self.name}] Installation prefix will be: {install_prefix}")

        with current_directory(build_dir):
            info(f"[{self.name}] Applying LT_SYS_SYMBOL_USCORE fix and m4 directory setup")
            m4_dir = join(build_dir, 'm4')
            if not exists(m4_dir):
                os.makedirs(m4_dir)
            this_recipe_dir = os.path.dirname(__file__)
            project_m4_file = join(this_recipe_dir, '..', '..', 'm4', 'lt_sys_symbol_uscore.m4')
            if not exists(project_m4_file):
                raise RuntimeError(f"[{self.name}] CRITICAL: m4 macro file {project_m4_file} not found.")
            sh.cp("-f", project_m4_file, join(m4_dir, 'lt_sys_symbol_uscore.m4'))
            info(f"[{self.name}] Copied lt_sys_symbol_uscore.m4 to {m4_dir}/")

            # Patch configure.ac or configure.in to include required m4 macros
            configure_ac_path = join(build_dir, 'configure.ac')
            configure_in_path = join(build_dir, 'configure.in')
            if exists(configure_ac_path):
                target_configure_file = configure_ac_path
            elif exists(configure_in_path):
                target_configure_file = configure_in_path
            else:
                # If neither exists, try running autogen.sh to generate them
                if exists(join(build_dir, 'autogen.sh')):
                    info(f"[{self.name}] Neither configure.ac nor configure.in found. Running autogen.sh first.")
                    try:
                        shprint(sh.Command('./autogen.sh'), _env=env)
                    except Exception as e:
                        warning(f"[{self.name}] autogen.sh initially failed or had warnings: {e}.")
                    if exists(configure_ac_path):
                        target_configure_file = configure_ac_path
                    elif exists(configure_in_path):
                        target_configure_file = configure_in_path
                    else:
                        raise FileNotFoundError(f"[{self.name}] configure.ac/in not found even after running autogen.sh")
                else:
                    raise FileNotFoundError(f"[{self.name}] {configure_ac_path} (or .in) not found, and no autogen.sh available.")

            # Insert m4_pattern_allow and AC_CONFIG_MACRO_DIRS after AC_INIT if not present
            info(f"[{self.name}] Patching {target_configure_file}")
            with open(target_configure_file, 'r') as f:
                original_lines = f.readlines()

            lines = list(original_lines)
            has_m4_pattern_allow = any(re.search(r"m4_pattern_allow\s*\(\s*\[LT_SYS_SYMBOL_USCORE\]\s*\)", line_content) for line_content in lines)
            has_ac_config_macro_dirs = any(re.search(r"AC_CONFIG_MACRO_DIRS?\s*\(\s*\[m4\]\s*\)", line_content) for line_content in lines)

            ac_init_index = -1
            for i, line_content in enumerate(lines):
                if line_content.strip().startswith("AC_INIT"):
                    ac_init_index = i
                    break

            modified_configure_ac = False
            if ac_init_index != -1:
                lines_inserted_count = 0
                if not has_m4_pattern_allow:
                    lines.insert(ac_init_index + 1 + lines_inserted_count, 'm4_pattern_allow([LT_SYS_SYMBOL_USCORE])\n')
                    lines_inserted_count += 1
                    modified_configure_ac = True
                    info(f"[{self.name}] Inserted m4_pattern_allow.")
                if not has_ac_config_macro_dirs:
                    lines.insert(ac_init_index + 1 + lines_inserted_count, 'AC_CONFIG_MACRO_DIRS([m4])\n')
                    modified_configure_ac = True
                    info(f"[{self.name}] Inserted AC_CONFIG_MACRO_DIRS.")
            else:
                warning(f"[{self.name}] AC_INIT not found in {target_configure_file}. Cannot reliably patch.")

            if modified_configure_ac:
                with open(target_configure_file, 'w') as f:
                    f.writelines(lines)
                info(f"[{self.name}] Successfully patched {target_configure_file}.")
            else:
                info(f"[{self.name}] {target_configure_file} already contained necessary m4 directives or AC_INIT not found.")

            # Remove old autotools artifacts before regenerating
            for p_name in ['configure', 'aclocal.m4', 'autom4te.cache']:
                p_path = join(build_dir, p_name)
                if exists(p_path):
                    info(f"[{self.name}] Removing existing autotools artifact: {p_path}")
                    if os.path.isdir(p_path) and not os.path.islink(p_path):
                        sh.rm("-rf", p_path)
                    else:
                        os.remove(p_path)

            # Regenerate autotools files
            info(f"[{self.name}] Running autoreconf -vif to regenerate build files with patches...")
            shprint(sh.Command('autoreconf'), '-vif', _env=env)

            # Configure, build, and install
            info(f"[{self.name}] Running libffi configure script...")
            configure_cmd = sh.Command('./configure')
            if not hasattr(self.ctx, 'ndk') or not hasattr(self.ctx.ndk, 'llvm_prebuilt_dir'):
                raise AttributeError(f"Context (self.ctx.ndk) missing 'llvm_prebuilt_dir'. NDK obj: {getattr(self.ctx, 'ndk', 'Not found')}")
            sysroot_path = join(self.ctx.ndk.llvm_prebuilt_dir, 'sysroot')
            info(f"[{self.name}] Using sysroot: {sysroot_path}")
            shprint(configure_cmd,
                    '--host=' + arch.command_prefix,
                    '--prefix=' + install_prefix,
                    '--enable-shared',
                    '--disable-static',
                    '--with-sysroot=' + sysroot_path,
                    _env=env)

            info(f"[{self.name}] Building libffi...")
            jobs = cpu_count()
            info(f"[{self.name}] make -j{jobs}")
            shprint(sh.make, f'-j{jobs}', _env=env)

            info(f"[{self.name}] Installing libffi...")
            shprint(sh.make, 'install', _env=env)

    def get_include_dirs(self, arch_iface):
        """
        Returns a list of include directories for the given architecture.
        Checks that the critical headers are present after install.
        """
        arch_obj, arch_name = self._get_arch_obj_and_name(arch_iface)
        install_prefix = self.ctx.get_python_install_dir(arch_obj.arch)
        primary_include = join(install_prefix, 'include')

        # Warn if headers are missing
        if not (exists(join(primary_include, 'ffi.h')) and exists(join(primary_include, 'ffitarget.h'))):
            warning(f"[{self.name}] CRITICAL HEADERS MISSING: ffi.h or ffitarget.h not found in {primary_include} for arch {arch_name}. This WILL cause issues for _ctypes.")

        includes = [primary_include]
        info(f"[{self.name}] Providing include dirs for arch {arch_name}: {includes}")
        return includes

    def get_lib_dirs(self, arch_iface):
        """
        Returns a list of library directories for the given architecture.
        """
        arch_obj, arch_name = self._get_arch_obj_and_name(arch_iface)
        install_prefix = self.ctx.get_python_install_dir(arch_obj.arch)
        lib_path = join(install_prefix, 'lib')
        info(f"[{self.name}] Providing lib dir for arch {arch_name}: {[lib_path]}")
        return [lib_path]

    def get_libraries(self, arch_iface):
        """
        Returns a list of library names to link against for the given architecture.
        """
        arch_obj, arch_name = self._get_arch_obj_and_name(arch_iface)
        libs = ['ffi']
        info(f"[{self.name}] Providing library names for arch {arch_name}: {libs}")
        return libs

    def get_pkgconfig_dirs(self, arch_iface):
        """
        Returns a list of pkg-config directories for the given architecture.
        """
        arch_obj, arch_name = self._get_arch_obj_and_name(arch_iface)
        install_prefix = self.ctx.get_python_install_dir(arch_obj.arch)
        pkgconfig_dir = join(install_prefix, 'lib', 'pkgconfig')
        info(f"[{self.name}] Providing pkgconfig dir for arch {arch_name}: {[pkgconfig_dir]}")
        return [pkgconfig_dir]

recipe = LibFFIRecipe()