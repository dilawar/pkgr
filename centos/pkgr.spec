
Name:     pkgr
Version:  0.1.0
Release:  1%{?dist}
Summary:  Package Linux pacakges

License: GNUv3
URL: https://github.com/dilawar/pkgr
Source0:  .

BuildRequires: python39-devel



%description
./README.md

%prep
%autosetup

%build
%configure
%make_build

%install
cd build && make install DESTDIR="${BP_DESTDIR}"

%files


%changelog

