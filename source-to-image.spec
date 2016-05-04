#debuginfo not supported with Go
%global debug_package %{nil}
# modifying the Go binaries breaks the DWARF debugging
%global __os_install_post %{_rpmconfigdir}/brp-compress

%global gopath      %{_datadir}/gocode

# docker_version is the version of docker requires by packages
%global docker_version 1.6

Name:           source-to-image
# Version is not kept up to date and is intended to be set by tito custom
# builders provided in the .tito/lib directory of this project
Version:        0.0.2
Release:        1%{?dist}
Summary:        source-to-image (s2i) a tool for building reproducible Docker images.
License:        ASL 2.0
URL:            https://github.com/openshift/%{name}
ExclusiveArch:  x86_64
Source0:        https://%{import_path}/archive/v%{version}.tar.gz
BuildRequires:  systemd
BuildRequires:  golang >= 1.4
Requires:       docker >= %{docker_version}
Requires:       iptables

#
# The following Bundled Provides entries are populated automatically by the
# OpenShift source-to-image tito custom builder found here:
#   https://github.com/openshift/source-to-image/blob/master/.tito/lib/s2i/builder/
#
# These are defined as per:
# https://fedoraproject.org/wiki/Packaging:Guidelines#Bundling_and_Duplication_of_system_libraries
#
### AUTO-BUNDLED-GEN-ENTRY-POINT

%description
Source-to-image (s2i) is a tool for building reproducible Docker images. s2i
produces ready-to-run images by injecting source code into a Docker image and
assembling a new Docker image which incorporates the builder image and built
source. The result is then ready to use with docker run. s2i supports
incremental builds which re-use previously downloaded dependencies, previously
built artifacts, etc.

%prep
%setup -q -n %{name}-%{version}

%build
make

%install

source <(go env)

install -d %{buildroot}%{_bindir}
# Install components
for bin in s2i
do
  echo "+++ INSTALLING ${bin}"
  install -p -m 755 _output/local/bin/linux/$GOARCH/${bin} %{buildroot}%{_bindir}/${bin}
done

install -d %{_sysconfdir}/bash_competion.d
install -p -m 644 contrib/bash/s2i %{_sysconfdir}/bash_completion.d/s2i

%check
make check

%files
%doc README.md
%license LICENSE
%{_bindir}/s2i
%{_sysconfdir}/bash_completion.d/s2i

%changelog
* Wed May 04 2016 Adam Miller <maxamillion@fedoraproject.org> 0.0.2-1
- new package built with tito

* Wed May 04 2016 Adam Miller <maxamillion@fedoraproject.org> - 0.0.1-1
- First package build
