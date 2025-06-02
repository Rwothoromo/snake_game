# recipes/libffi/__init__.py
from pythonforandroid.recipe import Recipe
from pythonforandroid.logger import shprint, info, warning
from pythonforandroid.util import current_directory
import sh
import os
from os.path import join, exists

class LibFFIRecipe(Recipe):
    name = 'libffi'
    version = '3.4.4' # Common version, adjust if p4a expects differently
    url = 'https://github.com/libffi/libffi/releases/download/v{version}/libffi-{version}.tar.gz'
    
    # If your p4a's libffi recipe had specific patches, you might need to add them here too.
    # patches = ['some-patch-from-p4a.patch', 'another.patch']

    def should_build(self, arch):
        # This ensures it rebuilds if the recipe itself changes, which is useful during debugging.
        # For production, you might remove or refine this.
        return True 

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)
        build_dir = self.get_build_dir(arch.arch)

        with current_directory(build_dir):
            info(f"[{self.name}] Applying LT_SYS_SYMBOL_USCORE fix")
            
            # 1. Ensure m4 directory exists
            m4_dir = join(build_dir, 'm4')
            if not exists(m4_dir):
                os.makedirs(m4_dir)

            # 2. Copy lt_sys_symbol_uscore.m4 from project root to libffi's m4 dir
            #    The path is relative from this recipe file to the project's m4 dir.
            #    recipes/libffi/__init__.py -> ../../m4/lt_sys_symbol_uscore.m4
            this_recipe_dir = os.path.dirname(__file__)
            project_m4_file = join(this_recipe_dir, '..', '..', 'm4', 'lt_sys_symbol_uscore.m4')
            
            if not exists(project_m4_file):
                raise RuntimeError(f"[{self.name}] CRITICAL: m4 macro file not found at {project_m4_file}")
            
            sh.cp("-f", project_m4_file, join(m4_dir, 'lt_sys_symbol_uscore.m4'))
            info(f"[{self.name}] Copied lt_sys_symbol_uscore.m4 to {m4_dir}/")

            # 3. Patch configure.ac (or configure.in)
            configure_ac_path = join(build_dir, 'configure.ac')
            if not exists(configure_ac_path):
                configure_ac_path = join(build_dir, 'configure.in') # Some older versions use .in
            
            if not exists(configure_ac_path):
                 # If neither configure.ac nor autogen.sh exists, it's an issue.
                 # However, autogen.sh usually generates configure.ac
                if exists(join(build_dir, 'autogen.sh')):
                    info(f"[{self.name}] configure.ac not found. Will run autogen.sh first.")
                    # Run autogen.sh which should create configure.ac
                    try:
                        shprint(sh.Command('./autogen.sh'), _env=env)
                    except Exception as e:
                        warning(f"[{self.name}] autogen.sh initially failed or had warnings: {e}. Proceeding to check for configure.ac.")
                    if not exists(configure_ac_path): # Re-check after autogen.sh
                         configure_ac_path_check = join(build_dir, 'configure.ac') # Default name
                         if not exists(configure_ac_path_check):
                            raise FileNotFoundError(f"[{self.name}] {configure_ac_path_check} not found even after running autogen.sh")
                         configure_ac_path = configure_ac_path_check # Update path if created
                else:
                    raise FileNotFoundError(f"[{self.name}] {configure_ac_path} (or .in) not found, and no autogen.sh available.")
            
            info(f"[{self.name}] Patching {configure_ac_path}")
            with open(configure_ac_path, 'r') as f:
                lines = f.readlines()
            
            new_lines = []
            patched_m4_pattern = any("m4_pattern_allow([LT_SYS_SYMBOL_USCORE])" in line for line in lines)
            patched_m4_dirs = any("AC_CONFIG_MACRO_DIRS([m4])" in line for line in lines)
            
            inserted = False
            for line in lines:
                new_lines.append(line)
                if not inserted and line.strip().startswith('AC_INIT'):
                    if not patched_m4_pattern:
                        new_lines.append('m4_pattern_allow([LT_SYS_SYMBOL_USCORE])\n')
                    if not patched_m4_dirs:
                        new_lines.append('AC_CONFIG_MACRO_DIRS([m4])\n')
                    inserted = True
            
            if not patched_m4_pattern or not patched_m4_dirs:
                with open(configure_ac_path, 'w') as f:
                    f.writelines(new_lines)
                info(f"[{self.name}] Patched {configure_ac_path} for LT_SYS_SYMBOL_USCORE.")
            else:
                info(f"[{self.name}] {configure_ac_path} already contains m4 directives.")

            # 4. Run autogen.sh if it exists and configure script is not present, or just autoreconf
            #    The p4a recipe for libffi (from which your log comes) calls:
            #    shprint(sh.Command('autoreconf'), '-vif', _env=env)
            #    This implies it doesn't find/prioritize autogen.sh or autogen.sh is not part of this version's flow.
            #    So, we will directly call autoreconf.
            
            info(f"[{self.name}] Running autoreconf -vif to regenerate build files with patches...")
            shprint(sh.Command('autoreconf'), '-vif', _env=env)
            
            info(f"[{self.name}] Running libffi configure script...")
            # Standard configure flags for libffi in p4a
            configure_cmd = sh.Command('./configure')
            shprint(configure_cmd,
                    '--host=' + arch.command_prefix,
                    '--prefix=' + self.ctx.get_python_install_dir(arch.arch), # Installs into python's dist
                    '--enable-shared',
                    '--disable-static', 
                    '--with-sysroot=' + self.ctx.ndk_platform, # Essential for cross-compilation
                    _env=env)
            
            info(f"[{self.name}] Building libffi...")
            shprint(sh.make, '-j', str(self.ctx.concurrent_tasks), _env=env)
            
            info(f"[{self.name}] Installing libffi...")
            shprint(sh.make, 'install', _env=env)

recipe = LibFFIRecipe()