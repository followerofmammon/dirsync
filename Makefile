install:
	sudo pip install -U -r requirements.txt
	sudo python setup.py install

check_convention:
	pep8 dirsync

clean:
	rm -rf AUTHORS build ChangeLog dirsync.egg-info
