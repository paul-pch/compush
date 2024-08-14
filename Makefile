
all: install integrate

install:
	pyinstaller --onefile compush.py

integrate:
	grep -q '$(CURDIR)' ~/.zshrc || echo 'export PATH=$(CURDIR)/dist:$$PATH' >> ~/.zshrc
