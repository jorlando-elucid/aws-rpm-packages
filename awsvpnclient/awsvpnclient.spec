# Start method called with config file and management port password file contents.
# Ovpn binary calculated checksum: 506017103194649c81825504261fd0a24e20cb2dba5bb88cc9a4c91b1a52fa41.
# Ovpn binary actual checksum: 6719be8e3b8b6355a480fd605f385b7a627b2b59eed3f6357cfeb7c33a6b5a5b
# OvpnBinaryChecksumValidationFailed
# Disable stripping:
%define __spec_install_post /usr/lib/rpm/brp-compress || :

%define debug_package %{nil}
%define _build_id_links none
%undefine _auto_set_build_flags

%global __provides_exclude_from  /opt/awsvpnclient/.*\\.so
%global __requires_exclude_from  ^/opt/awsvpnclient/(.*\\.so|Resources/openvpn/.*)$

BuildArch:     x86_64
Name:          awsvpnclient
Version:       4.1.0
Release:       8
License:       ASL 2.0
Group:         Converted/misc
Summary:       AWS VPN Client
Source0:       https://d20adtppz83p9s.cloudfront.net/GTK/%{version}/awsvpnclient_amd64.deb
Source1:       70-awsvpnclient.preset
Patch0:        awsvpnclient.desktop.patch
Patch1:        configure-dns.patch
Patch2:        awsvpnclient.runtimeconfig.patch
Patch3:        awsvpnclient.deps.patch
Patch4:        acvc.gtk..deps.patch

BuildRequires: systemd-rpm-macros

%description
%{summary}

%prep
%setup -cT
ar p %{SOURCE0} data.tar.zst | tar --zstd -x
%patch -P 0 -p1
%patch -P 2 -p1
%patch -P 3 -p1
%patch -P 4 -p1

find . -iname "*.a" -delete
find . -iname "*.pdb" -delete
mv ./opt/%{name}/Service/Resources/openvpn       ./opt/%{name}/Resources/
mv ./opt/%{name}/Service/ACVC.GTK.Service{,.dll} ./opt/%{name}/
mv ./opt/%{name}/Service/*.json                  ./opt/%{name}/
rm -rf ./opt/%{name}/Service
rm -rf ./opt/%{name}/SQLite.Interop.dll # https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=awsvpnclient#n31
                                        # Workaround for missing compatibility of the SQL library with arch linux:
                                        # Intentionally break the metrics agent,
                                        # it will be unable to laod the dynamic lib and wont start but continue with error message
                                        # fixes errors:
                                        # gtk_tree_model_iter_nth_child: assertion 'n >= 0' failed
                                        # gtk_list_store_get_path: assertion 'iter->stamp == priv->stamp' failed
sed -i "s#/opt/awsvpnclient/Service/#/opt/awsvpnclient/#;" ./etc/systemd/system/%{name}.service
mv ./opt/%{name}/{AWS\ VPN\ Client,AWSVPNClient}
rm -rf \
       ./opt/%{name}/libmscordbi.so \
       ./opt/%{name}/libmscordaccore.so \
       ./opt/%{name}/libcoreclrtraceptprovider.so \
       ./opt/%{name}/createdump

%install
mv opt %{buildroot}/
%__install -Dpm 0644 usr/share/applications/awsvpnclient.desktop %{buildroot}%{_datadir}/applications/awsvpnclient.desktop
%__install -Dpm 0644 usr/share/doc/awsvpnclient/copyright        %{buildroot}%{_datadir}/doc/awsvpnclient/copyright
%__install -Dpm 0644 usr/share/pixmaps/acvc-64.png               %{buildroot}%{_datadir}/pixmaps/acvc-64.png

%__install -Dpm 0644 etc/systemd/system/%{name}.service          %{buildroot}%{_unitdir}/%{name}.service
%__install -Dpm 0644 %{SOURCE1}                                  %{buildroot}%{_presetdir}/70-%{name}.preset

%__install -d %{buildroot}/opt/%{name}/Service/Resources/openvpn
ln -s ../../../Resources/openvpn/configure-dns %{buildroot}/opt/%{name}/Service/Resources/openvpn/configure-dns
( cd %{buildroot}/opt/%{name}/Resources/openvpn/ && ./openssl fipsinstall -out fipsmodule.cnf -module ./fips.so )
ln -s ../../../Resources/openvpn/fipsmodule.cnf %{buildroot}/opt/%{name}/Service/Resources/openvpn/fipsmodule.cnf

mkdir -p %{buildroot}/usr/bin
ln -s /usr/sbin/ip %{buildroot}/usr/bin/ip

%clean

%files
%defattr(0644, root, root, 0755)
%attr(0755, root, root) "/opt/%{name}/AWSVPNClient"
%attr(0755, root, root) /opt/%{name}/Resources/openvpn/acvc-openvpn
%attr(0755, root, root) /opt/%{name}/Resources/openvpn/configure-dns
%attr(0755, root, root) /opt/%{name}/Resources/openvpn/openssl
%attr(0755, root, root) /opt/%{name}/Resources/openvpn/ld-musl-x86_64.so.1
%attr(0755, root, root) /opt/%{name}/Resources/openvpn/*.so
%attr(0755, root, root) /opt/%{name}/ACVC.GTK.Service
/opt/%{name}/*.dll
/opt/%{name}/*.dylib
/opt/%{name}/*/*.dll
/opt/%{name}/*.so
/opt/%{name}/Resources/openvpn/*.cnf
/opt/%{name}/*.json
/opt/%{name}/Resources/acvc-64.png

/usr/share/applications/%{name}.desktop
/usr/share/pixmaps/acvc-64.png
%{_presetdir}/70-%{name}.preset
%{_unitdir}/%{name}.service

/opt/%{name}/Service/Resources/openvpn/configure-dns
/opt/%{name}/Service/Resources/openvpn/fipsmodule.cnf

/usr/bin/ip

%license /opt/%{name}/Resources/LINUX-LICENSE.txt
%license /opt/%{name}/Resources/THIRD-PARTY-LICENSES-GTK.txt
%doc %{_docdir}/%{name}
%dir /opt/%{name}/
%dir /opt/%{name}/Resources/
%dir /opt/%{name}/Resources/openvpn
%dir /opt/%{name}/Service/
%dir /opt/%{name}/Service/Resources
%dir /opt/%{name}/Service/Resources/openvpn
%dir /opt/%{name}/de/
%dir /opt/%{name}/es/
%dir /opt/%{name}/fr/
%dir /opt/%{name}/it/
%dir /opt/%{name}/ja/
%dir /opt/%{name}/ko/
%dir /opt/%{name}/pt-BR/
%dir /opt/%{name}/zh-Hans/
%dir /opt/%{name}/zh-Hant/

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%changelog
* Sat Dec 21 2024 AV - 4.1.0-8
- added symlink for /usr/sbin/ip, because they have hash validation for at least configure-dns and acvc-openvpn

* Sat Nov 16 2024 AV - 4.1.0-7
- bumb version

* Thu Aug 1 2024 Cott Lang - 3.14.0-1
- Updated the OpenVPN and OpenSSL libraries.

* Mon May 27 2024 Anatolii Vorona - 3.13.0-1
- bump version
- Automatically reconnect when local area network ranges change.

* Mon Apr 29 2024 Cott Lang - 3.12.2-1
- bump version
- Resolved a SAML authentication issue with Chromium-based browsers since version 123.
- Improved security posture.
- Fixed connectivity issues for some LAN configurations.

* Sun Dec 10 2023 Anatolii Vorona - 3.11.0-1
- bump version
- improved accessibility

* Sat Aug 26 2023 Anatolii Vorona - 3.9.0-1
- bump version
- improved security posture
- fixed a connectivity issue when NAT64 is enabled in the client network
- minor bug fixes and enhancements
* Tue Mar 7 2023 Anatolii Vorona  3.4.0-1
- bump version
- disable Globalization. ICU is needed except if globalization is disabled
  Client works with libicu versions 67 and 69, and fc37 ships with libicu v71.

* Fri Jan 27 2023 Anatolii Vorona  3.2.0-1
- Added support for "verify-x509-name" OpenVPN flag.

* Tue Dec 13 2022 Anatolii Vorona  3.1.0-5
- configure-dns is working now

* Tue Jul 26 2022 Anatolii Vorona  3.1.0-2
- rebuild awsvpnclient_amd64.deb
- remove unused files
- remove createdump and its dependencies
