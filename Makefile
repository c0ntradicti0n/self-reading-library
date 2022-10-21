USER ?= $(shell id -u):$(shell id -g)

format: format-python format-react

format-python:
	python -m black python
format-react:
	cd react/layout_viewer/ && npm run format:fix


mount:
	sudo mount --bind ./python/.layouteagle/pdfs/ ./react/layout_viewer_made/public/pdfs  & sudo mount --bind ./python/.layouteagle/audio/ ./react/layout_viewer_made/public/audio

mount-osx:
	sudo bindfs  ./python/.layouteagle/pdfs/ ./react/layout_viewer_made/public/pdfs

.PHONY: dockerbuild
dockerbuild:
	CWD=$(shell pwd) DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker-compose build

.PHONY: dockerup
dockerup:
	CWD=$(shell pwd) UID="$(shell id -u)" GID="$(shell id -g)" DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain  docker-compose up -d

.PHONY: dockerdown
dockerdown:
	CWD=$(shell pwd) DOCKER_BUILDKIT=1 docker-compose down -v

.PHONY: dockerlogs
dockerlogs:
	docker logs -f rest

dockerdebug:
	docker exec -itd -p 2222:22 $SERVICE /usr/sbin/sshd -D

dbash:
	docker exec -it rest bash

d: dockerdown dockerbuild dockerup
ddb:
	CWD=$(shell pwd) UID="$(shell id -u)" GID="$(shell id -g)" DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain  docker-compose up -d db
sync:
	rsync -r --exclude 'node_modules' react/layout_viewer/* react/layout_viewer_made
fe:
	cd react/layout_viewer_made/ && yarn run dev


.PHONY: backend
backend:
	cd python && python backend.py

.PHONY: frontend
frontend: sync fe


docker-fill:
	docker-compose build fill && docker-compose up fill -d && docker logs -f fill
