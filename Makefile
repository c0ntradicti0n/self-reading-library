USER ?= $(shell id -u):$(shell id -g)

format: format-python format-react

format-python:
	python -m black python
format-react:
	cd react/layout_viewer_made/ && npm run format:fix


mount:
	sudo mount --bind ./python/.layouteagle/pdfs/ ./react/layout_viewer_made/public/pdfs  & sudo mount --bind ./python/.layouteagle/audio/ ./react/layout_viewer_made/public/audio

mount-osx:
	sudo bindfs  ./python/.layouteagle/pdfs/ ./react/layout_viewer_made/public/pdfs

build:
	USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker-compose build
build_fe:
	USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker-compose build fe

up:
	USER=$$USER CWD=$(shell pwd) UID="$(shell id -u)" GID="$(shell id -g)" DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain  docker-compose up -d

down:
	CWD=$(shell pwd) DOCKER_BUILDKIT=1 docker-compose down -v

dockerlogs:
	docker logs -f rest

dockerdebug:
	docker exec -itd rest /usr/sbin/sshd -D

dbash:
	docker exec -it rest bash

d: down dockerbuild up
ddb:
	CWD=$(shell pwd) UID="$(shell id -u)" GID="$(shell id -g)" DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain  docker-compose up -d db
sync:
	rsync -r --exclude 'node_modules' react/layout_viewer/* react/layout_viewer_made
fe:
	cd react/layout_viewer_made/ && yarn run dev




sync_from_host:
	rsync -av --progress  -r python/.layouteagle/ deploy@self-reading-library.science:/home/deploy/self-reading-library/python/.layouteagle/

sync_from_romote:
	rsync -av --progress  -r deploy@self-reading-library.science:/home/deploy/self-reading-library/python/.layouteagle/ python/.layouteagle/



backend:
	cd python && python backend.py

frontend: sync fe


docker-fill:
	docker-compose build fill && docker-compose up fill -d && docker logs -f fill
