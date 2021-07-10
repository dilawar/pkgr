PKGR := poetry run pkgr

all : create_pkg

create_pkg: pkgr.toml
	$(PKGR) rpm generate centos
	# $(PKGR) rpm build centos
