PKGR := pkgr

all : create_pkg

create_pkg: pkgr.toml
	$(PKGR) rpm build centos --arch noarch

lint:
	pylint -E pkgr/

test:
	docker run -it pkgr/build bash
