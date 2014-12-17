all: mk_resources mk_ui

mk_ui:
	$(MAKE) -C ui/

mk_resources:
	pyrcc4 res/icons.qrc > icons_rc.py
	sed -i s/\"/b\"/ icons_rc.py


