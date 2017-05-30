%global pecl_name LZF
%global ext_name lzf
%global php_base php56u
%global ini_name 40-%{ext_name}.ini

%bcond_without zts

Name: %{php_base}-pecl-%{ext_name}
Version: 1.6.6
Release: 1.ius%{?dist}
Summary: Extension to handle LZF de/compression
Group: Development/Languages
License: PHP
URL: http://pecl.php.net/package/%{pecl_name}
Source0: http://pecl.php.net/get/%{pecl_name}-%{version}.tgz

BuildRequires: %{php_base}-devel
BuildRequires: %{php_base}-pear
BuildRequires: liblzf-devel
Requires: php(zend-abi) = %{php_zend_api}
Requires: php(api) = %{php_core_api}
Requires(post): %{php_base}-pear
Requires(postun): %{php_base}-pear

# provide the stock name
Provides: php-pecl-%{ext_name} = %{version}
Provides: php-pecl-%{ext_name}%{?_isa} = %{version}

# provide the stock and IUS names without pecl
Provides: php-%{ext_name} = %{version}
Provides: php-%{ext_name}%{?_isa} = %{version}
Provides: %{php_base}-%{ext_name} = %{version}
Provides: %{php_base}-%{ext_name}%{?_isa} = %{version}

# provide the stock and IUS names in pecl() format
Provides: php-pecl(%{pecl_name}) = %{version}
Provides: php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides: %{php_base}-pecl(%{pecl_name}) = %{version}
Provides: %{php_base}-pecl(%{pecl_name})%{?_isa} = %{version}

# conflict with the stock name
Conflicts: php-pecl-%{ext_name} < %{version}

%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_provides_in: %filter_provides_in %{php_ztsextdir}/.*\.so$}
%{?filter_setup}


%description
This extension provides LZF compression and decompression using the liblzf
library

LZF is a very fast compression algorithm, ideal for saving space with a 
slight speed cost.


%prep
%setup -c -q
mv %{pecl_name}-%{version} NTS

sed -e '/name="lib/d' -i package.xml
rm -r NTS/lib/

sed -e 's/role="test"/role="src"/' \
    -e '/LICENSE/s/role="doc"/role="src"/' \
    -i package.xml

%if %{with zts}
cp -pr NTS ZTS
%endif

%{__cat} > %{ini_name} << 'EOF'
; Enable %{pecl_name} extension module
extension=%{ext_name}.so
EOF


%build
pushd NTS
phpize
%configure --enable-lzf --with-liblzf --with-php-config=%{_bindir}/php-config
%{__make} %{?_smp_mflags}
popd

%if %{with zts}
pushd ZTS
zts-phpize
%configure --enable-lzf --with-liblzf --with-php-config=%{_bindir}/zts-php-config
%{__make} %{?_smp_mflags}
popd
%endif


%install
%{__make} -C NTS install INSTALL_ROOT=%{buildroot}
%{__install} -D -p -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

%if %{with zts}
%{__make} -C ZTS install INSTALL_ROOT=%{buildroot}
%{__install} -D -p -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

%{__install} -D -p -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{pecl_name}.xml

for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -D -p -m 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
pushd NTS
TEST_PHP_EXECUTABLE=%{__php} \
REPORT_EXIT_STATUS=1 \
NO_INTERACTION=1 \
%{__php} run-tests.php \
    -n -q \
    -d extension=%{buildroot}%{php_extdir}/%{ext_name}.so
popd

%if %{with zts}
pushd ZTS
TEST_PHP_EXECUTABLE=%{__ztsphp} \
REPORT_EXIT_STATUS=1 \
NO_INTERACTION=1 \
%{__ztsphp} run-tests.php \
    -n -q \
    -d extension=%{buildroot}%{php_ztsextdir}/%{ext_name}.so
popd
%endif


%if 0%{?pecl_install:1}
%post
%{pecl_install} %{pecl_xmldir}/%{pecl_name}.xml >/dev/null || :
%endif


%if 0%{?pecl_uninstall:1}
%postun
if [ $1 -eq 0 ]; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi
%endif


%files
%{!?_licensedir:%global license %%doc}
%license NTS/LICENSE
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{pecl_name}.xml

%{php_extdir}/%{ext_name}.so
%config(noreplace) %{php_inidir}/%{ini_name}

%if %{with zts}
%{php_ztsextdir}/%{ext_name}.so
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%endif


%changelog
* Tue May 30 2017 Ben Harper <ben.harper@rackspace.com> - 1.6.6-1.ius
- Latest upstream

* Wed Aug 03 2016 Carl George <carl.george@rackspace.com> - 1.6.5-1.ius
- Port from Fedora to IUS
- Install package.xml as %%{pecl_name}.xml, not %%{name}.xml
- Install LICENSE
- Install doc files in %%{pecl_docdir}
- Enable ZTS

* Mon Jun 27 2016 Remi Collet <remi@fedoraproject.org> - 1.6.5-1
- update to 1.6.5
- rebuild for https://fedoraproject.org/wiki/Changes/php70

* Thu Feb 25 2016 Remi Collet <remi@fedoraproject.org> - 1.6.2-11
- drop scriptlets (replaced by file triggers in php-pear) #1310546

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.6.2-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.2-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.2-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Jun 19 2014 Remi Collet <rcollet@redhat.com> - 1.6.2-7
- rebuild for https://fedoraproject.org/wiki/Changes/Php56
- add numerical prefix to extension configuration file

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Mar 22 2013 Remi Collet <rcollet@redhat.com> - 1.6.2-4
- rebuild for http://fedoraproject.org/wiki/Features/Php55

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Oct 28 2012 Andrew Colin Kissa - 1.6.2-2
- Fix php spec macros
- Fix Zend API version checks

* Sat Oct 20 2012 Andrew Colin Kissa - 1.6.2-1
- Upgrade to latest upstream
- Fix bugzilla #838309 #680230

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jan 19 2012 Remi Collet <remi@fedoraproject.org> - 1.5.2-9
- rebuild against PHP 5.4, with upstream patch
- add filter to avoid private-shared-object-provides
- add minimal %%check

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Fri Jul 15 2011 Andrew Colin Kissa <andrew@topdog.za.net> - 1.5.2-7
- Fix bugzilla #715791

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Sun Jul 12 2009 Remi Collet <Fedora@FamilleCollet.com> - 1.5.2-4
- rebuild for new PHP 5.3.0 ABI (20090626)

* Mon Jun 22 2009 Andrew Colin Kissa <andrew@topdog.za.net> - 1.5.2-3
- Consistent use of macros

* Mon Jun 22 2009 Andrew Colin Kissa <andrew@topdog.za.net> - 1.5.2-2
- Fixes to the install to retain timestamps and other fixes raised in review

* Sun Jun 14 2009 Andrew Colin Kissa <andrew@topdog.za.net> - 1.5.2-1
- Initial RPM package
