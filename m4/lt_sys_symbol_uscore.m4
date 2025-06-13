AC_DEFUN([LT_SYS_SYMBOL_USCORE], [
  AC_REQUIRE([AC_CANONICAL_HOST])
  AC_CACHE_CHECK([for underscore in symbols], [lt_cv_sys_symbol_underscore],
    [lt_cv_sys_symbol_underscore=no
     AC_LINK_IFELSE([AC_LANG_PROGRAM([], [int foo() { return 0; }])],
       [lt_cv_sys_symbol_underscore=yes], [lt_cv_sys_symbol_underscore=no])])
  if test "x$lt_cv_sys_symbol_underscore" = "xyes"; then
    sys_symbol_underscore=yes
  else
    sys_symbol_underscore=no
  fi
  AC_SUBST([sys_symbol_underscore])
])
