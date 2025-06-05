# In your project's recipes/python3/__init__.py

# Make sure to import Recipe if you are using Recipe.get_recipe()
from pythonforandroid.recipe import Recipe 
from os.path import join # if not already imported

# If you're inheriting:
# from pythonforandroid.recipes.python3 import Python3Recipe as OriginalPython3Recipe 
# class Python3Recipe(OriginalPython3Recipe):

# If you're copying the whole class:
class Python3Recipe(Recipe): # Or whatever it inherits from in your p4a version
    # ... (name, version, url, depends, etc. from original python3 recipe) ...
    # ... (all other methods from original python3 recipe) ...

    def build_arch(self, arch):
        # ... (original content of build_arch from p4a's python3 recipe) ...
        
        env = self.get_recipe_env(arch) # This should prepare CFLAGS, LDFLAGS etc.

        # --- BEGIN MODIFICATION for PKG_CONFIG_PATH ---
        info("Attempting to prepend correct libffi pkgconfig path for Python3 configure")
        libffi_recipe = Recipe.get_recipe('libffi', self.ctx)
        if hasattr(libffi_recipe, 'get_pkgconfig_dirs'):
            libffi_pkgconfig_dirs = libffi_recipe.get_pkgconfig_dirs(arch)
            if libffi_pkgconfig_dirs:
                # Prepend our libffi's pkgconfig path to make sure it's found first
                current_pkg_config_path = env.get('PKG_CONFIG_PATH', '')
                new_pkg_config_path = os.pathsep.join(libffi_pkgconfig_dirs)
                if current_pkg_config_path:
                    new_pkg_config_path += os.pathsep + current_pkg_config_path
                
                env['PKG_CONFIG_PATH'] = new_pkg_config_path
                info(f"Modified PKG_CONFIG_PATH for Python3 configure: {env['PKG_CONFIG_PATH']}")
            else:
                warning("LibFFI recipe provided no pkgconfig_dirs.")
        else:
            warning("LibFFI recipe has no get_pkgconfig_dirs method.")
        # --- END MODIFICATION ---

        # The rest of the build_arch method, including the configure call:
        with current_directory(self.get_build_dir(arch.arch)): # Or specific android-build subdir
            # ...
            # configure_cmd = self.get_configure_cmd(env, arch) 
            # configure_args = self.get_configure_args(arch, env)
            # shprint(configure_cmd, *configure_args, _env=env)
            # Make sure the above lines match how your p4a version calls configure.
            # The exact call is in the error log:
            # RAN: /home/builduser/app/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/python3/arm64-v8a__ndk_target_23/python3/configure ...
            
            configure_executable = join(self.get_build_dir(arch.arch), 'configure') # Path to python's configure
            # The args are from the log:
            configure_args = [
                '--host=aarch64-linux-android',
                '--build=x86_64-pc-linux-gnu',
                '--enable-shared',
                '--enable-ipv6',
                'ac_cv_file__dev_ptmx=yes',
                'ac_cv_file__dev_ptc=no',
                '--without-ensurepip',
                'ac_cv_little_endian_double=yes',
                'ac_cv_header_sys_eventfd_h=no',
                f'--prefix={self.ctx.get_python_install_dir(arch.arch)}', # Use actual install prefix
                f'--exec-prefix={self.ctx.get_python_install_dir(arch.arch)}',
                '--enable-loadable-sqlite-extensions',
                # '--with-build-python' is often problematic/unnecessary if PYTHON_FOR_BUILD is set
                # We can try removing it or ensuring PYTHON_FOR_BUILD is correctly in env
                # For now, let's keep it as per the log
                f'--with-build-python={self.ctx.hostpython}', 
                f'--with-openssl={Recipe.get_recipe("openssl", self.ctx).get_build_dir(arch.arch)}'
            ]
            # The configure executable is usually in the source dir, not android-build,
            # and android-build is where we run it *from*.
            python_source_dir = self.get_build_dir(arch.arch) # This is where configure lives
            
            # Change to the android-build subdirectory before running configure
            android_build_dir = join(python_source_dir, 'android-build')
            if not exists(android_build_dir):
                os.makedirs(android_build_dir)

            with current_directory(android_build_dir):
                # Path to configure is now ../configure if we are in android-build
                configure_executable_relpath = join('..', 'configure')
                shprint(sh.Command(configure_executable_relpath),
                        *configure_args,
                        _env=env)


        # ... (rest of the original build_arch method - make, make install etc.)
recipe = Python3Recipe()