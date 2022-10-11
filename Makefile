USER ?= $(shell id -u):$(shell id -g)

.PHONY: format
format:
	python -m black python

.PHONY: mount
mount:
	sudo mount --bind ./python/.layouteagle/pdfs/ ./react/layout_viewer_made/public/pdfs  & sudo mount --bind ./python/.layouteagle/audio/ ./react/layout_viewer_made/public/audio

.PHONY: dockerbuild
dockerbuild:
	DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker-compose build

.PHONY: dockerup
dockerup:
	CWD=$(shell pwd) UID="$(shell id -u)" GID="$(shell id -g)" DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain  docker-compose up -d

.PHONY: dockerdown
dockerdown:
	DOCKER_BUILDKIT=1 docker-compose down -v

.PHONY: dockerlogs
dockerlogs:
	docker logs -f rest

dockerdebug:
	docker exec -itd -p 2222:22 $SERVICE /usr/sbin/sshd -D


docker: dockerdown dockerbuild dockerup

.PHONY: backend
backend:
	cd python && python backend.py

.PHONY: frontend
frontend:
	cd react/layout_viewer_made/ && yarn run dev

docker-fill:
	docker-compose build fill && docker-compose up fill -d && docker logs -f fill
