install:
	sudo python setup.py install

check_convention:
	pep8 dirsync
