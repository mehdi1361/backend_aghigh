PROJECT_NAME=dashboard
APPS_DIRECTORY=apps
ENV=local
APP_NAME=
APP_FULLNAME=$(APPS_DIRECTORY).$(APP_NAME)
SETTINGS_FILE=$(PROJECT_NAME)/settings/base.py

export DJANGO_SETTINGS_MODULE := $(PROJECT_NAME).settings.$(ENV)

RMQ=rabbitmq-server
FLOWER_PORT=5555
LINUX_PACKAGE_MANAGER=apt-get
PAGS = $(RMQ) vim gawk
REQ_FILE=requirements.txt

startapp:
	mkdir -p $(APPS_DIRECTORY)/$(APP_NAME) 
	python manage.py $@ $(APP_NAME) $(APPS_DIRECTORY)/$(APP_NAME) --settings=$(PROJECT_NAME).settings.$(ENV)
	sed -i 's/$(APP_NAME)/$(APP_FULLNAME)/g' $(APPS_DIRECTORY)/$(APP_NAME)/apps.py
	gawk -i inplace '/INSTALLED_APPS \= \[/{print;print "    '\''$(APP_FULLNAME)'\'',";next}1' $(SETTINGS_FILE) 

freeze_requirements:
	pip freeze > $(REQ_FILE) 

install_requirements:
	pip install -r $(REQ_FILE)

make_messages:
	python manage.py makemessages -l fa_IR --settings=$(PROJECT_NAME).settings.$(ENV)

compile_messages:
	python manage.py compilemessages --settings=$(PROJECT_NAME).settings.$(ENV)

migrate:
	python manage.py $@ --settings=$(PROJECT_NAME).settings.$(ENV) $(APP_NAME)

runserver:
	python manage.py $@ 0:8000 --settings=$(PROJECT_NAME).settings.$(ENV)

makemigrations:
	python manage.py $@ --settings=$(PROJECT_NAME).settings.$(ENV) $(APP_NAME)

createsuperuser:
	python manage.py $@ --settings=$(PROJECT_NAME).settings.$(ENV)

run_celery:
	celery -A $(PROJECT_NAME) worker -l info -E -B 

run_celery_beat:
	celery -A $(PROJECT_NAME) beat

run_flower:
	flower -A $(PROJECT_NAME) --port=$(FLOWER_PORT)

install:
	sudo $(LINUX_PACKAGE_MANAGER) install $(PAGS)
	virtualenv ../env_$(PROJECT_NAME)
	source ../env/bin/active
	pip install -r $(REQ_FILE) 
