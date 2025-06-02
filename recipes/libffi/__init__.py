# recipes/libffi/__init__.py
from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint, info, warning
from pythonforandroid.util import current_directory
import sh
import os
from os.path import join, exists
import re # For more robust checking

class LibFFIRecipe(Recipe):
    name = 'libffi'
    version = '3.4.4' 
    url = 'https://github.com/libffi/libffi/releases/download/v{version}/libffi-{version}.tar.gz'
    
    # Set this to True to force a rebuild of this recipe, good for debugging
    # For production, you might remove or set to False
    # self.force_rebuild = True 

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        # If you need to clean up previous build attempts for this recipe specifically
        # build_dir = self.get_build_dir(arch.arch)
        # if os.path.exists(build_dir):
        #     info(f"[{self.name}] Cleaning previous build directory: {build_dir}")
        #     sh.rm("-rf", build_dir)

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        build_dir = self.get_build_dir(arch.arch)

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

            configure_ac_path = join(build_dir, 'configure.ac')
            configure_in_path = join(build_dir, 'configure.in')

            if exists(configure_ac_path):
                target_configure_file = configure_ac_path
            elif exists(configure_in_path):
                target_configure_file = configure_in_path
            else:
                if exists(join(build_dir, 'autogen.sh')):
                    info(f"[{self.name}] Neither configure.ac nor configure.in found. Running autogen.sh first.")
                    try:
                        shprint(sh.Command('./autogen.sh'), _env=env)
                    except Exception as e:
                        warning(f"[{self.name}] autogen.sh initially failed or had warnings: {e}.")
                    # Re-check after autogen.sh
                    if exists(configure_ac_path): target_configure_file = configure_ac_path
                    elif exists(configure_in_path): target_configure_file = configure_in_path
                    else: raise FileNotFoundError(f"[{self.name}] configure.ac/in not found even after running autogen.sh")
                else:
                    raise FileNotFoundError(f"[{self.name}] {configure_ac_path} (or .in) not found, and no autogen.sh available.")

            info(f"[{self.name}] Patching {target_configure_file}")
            with open(target_configure_file, 'r') as f:
                original_lines = f.readlines()
            
            lines = list(original_lines) # Work on a copy

            # Check for existing directives using regex for flexibility
            has_m4_pattern_allow = any(re.search(r"m4_pattern_allow\s*\(\s*\[LT_SYS_SYMBOL_USCORE\]\s*\)", line) for line in lines)
            has_ac_config_macro_dirs = any(re.search(r"AC_CONFIG_MACRO_DIRS?\s*\(\s*\[m4\]\s*\)", line) for line in lines) # Check for DIRS and DIR

            # Find AC_INIT and insert after it if directives are missing
            ac_init_index = -1
            for i, line in enumerate(lines):
                if line.strip().startswith("AC_INIT"):
                    ac_init_index = i
                    break
            
            modified_configure_ac = False
            if ac_init_index != -1:
                insert_index = ac_init_index + 1
                if not has_m4_pattern_allow:
                    lines.insert(insert_index, 'm4_pattern_allow([LT_SYS_SYMBOL_USCORE])\n')
                    modified_configure_ac = True
                    info(f"[{self.name}] Inserted m4_pattern_allow.")
                if not has_ac_config_macro_dirs:
                    # Insert after m4_pattern_allow if it was just added, or at same position
                    current_insert_idx = insert_index + (1 if not has_m4_pattern_allow and modified_configure_ac else 0)
                    lines.insert(current_insert_idx, 'AC_CONFIG_MACRO_DIRS([m4])\n')
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
            
            # Before running autoreconf, ensure configure script is removed if it exists,
            # to force its regeneration from the (potentially) modified configure.ac
            configure_script_path = join(build_dir, 'configure')
            if exists(configure_script_path):
                info(f"[{self.name}] Removing existing configure script to force regeneration: {configure_script_path}")
                os.remove(configure_script_path)
            
            # Some projects (especially older ones) might have `aclocal.m4` that needs removal too
            aclocal_m4_path = join(build_dir, 'aclocal.m4')
            if exists(aclocal_m4_path):
                info(f"[{self.name}] Removing existing aclocal.m4 to force regeneration: {aclocal_m4_path}")
                os.remove(aclocal_m4_path)
            
            # Also remove autom4te.cache if it exists
            autom4te_cache_path = join(build_dir, 'autom4te.cache')
            if exists(autom4te_cache_path):
                info(f"[{self.name}] Removing existing autom4te.cache: {autom4te_cache_path}")
                sh.rm("-rf", autom4te_cache_path)


            info(f"[{self.name}] Running autoreconf -vif to regenerate build files with patches...")
            # The -I m4 flag for aclocal is usually handled by AC_CONFIG_MACRO_DIRS.
            # autoreconf should pick up the m4 directory.
            shprint(sh.Command('autoreconf'), '-vif', _env=env) 
            
            info(f"[{self.name}] Running libffi configure script...")
            configure_cmd = sh.Command('./configure')
            shprint(configure_cmd,
                    '--host=' + arch.command_prefix,
                    '--prefix=' + self.ctx.get_python_install_dir(arch.arch),
                    '--enable-shared',
                    '--disable-static', 
                    '--with-sysroot=' + self.ctx.ndk_platform,
                    _env=env)
            
            info(f"[{self.name}] Building libffi...")
            shprint(sh.make, '-j', str(self.ctx.concurrent_tasks), _env=env)
            
            info(f"[{self.name}] Installing libffi...")
            shprint(sh.make, 'install', _env=env)

recipe = LibFFIRecipe()