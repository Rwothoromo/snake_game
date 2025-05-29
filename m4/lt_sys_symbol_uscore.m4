dnl LT_SYS_SYMBOL_USCORE
dnl -----------------
AC_DEFUN([LT_SYS_SYMBOL_USCORE],
[symcode='[ABCDGISTW]'
AC_REQUIRE([AC_CANONICAL_HOST])dnl
case $host_os in
aix*)
  symcode='[ABCDGISTW]'
  ;;
cygwin* | mingw* | pw32* | cegcc*)
  symcode='[ABCDGISTW]'
  ;;
hpux*)
  if test "$host_cpu" = ia64; then
    symcode='[ABCDGRST]'
  fi
  ;;
irix* | nonstopux*)
  symcode='[ABCDGIST]'
  ;;
osf*)
  symcode='[ABCDGQST]'
  ;;
solaris*)
  symcode='[ABCDGIST]'
  ;;
sco3.2v5*)
  symcode='[DT]'
  ;;
sysv4.2uw2*)
  symcode='[DT]'
  ;;
sysv5* | sco5v6* | unixware* | OpenUNIX*)
  symcode='[ABDT]'
  ;;
sysv4)
  symcode='[DFNSTU]'
  ;;
esac
objext=no
AC_CHECK_TOOL([OBJDUMP], [objdump], [objdump])
if test -n "$OBJDUMP"; then
  AC_CACHE_CHECK([for underscore prefix in symbols], [lt_cv_sys_symbol_underscore], [dnl
  cat > conftest.$ac_ext <<EOF
void nm_test_func(){}
int main(){nm_test_func();return 0;}
