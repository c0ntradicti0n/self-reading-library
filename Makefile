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

prod:
	ENV=prod USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker-compose build
dev:
	ENV=dev USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker-compose build
build:
	USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker-compose build
build_fe:
	USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker-compose build fe
over:
	ENV=prod USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker-compose -f docker-compose.override.yaml  build
overup:
	ENV=prod USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker-compose -f docker-compose.override.yaml  up
overdown:
	ENV=prod USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker-compose -f docker-compose.override.yaml down

CWD=$(shell pdw)
scrape_test:
	ENV=prod USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker run -v "$(shell pwd)/python:/home/finn/Programming/self-reading-library/python" full_python python3 core/standard_converter/Scraper.py


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
gdb:
	CWD=$(shell pwd) UID="$(shell id -u)" GID="$(shell id -g)" DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain  docker-compose up -d gdb

fe:
	cd react/layout_viewer_made/ && yarn run dev


docker-fill:
	docker-compose build fill && docker-compose up fill -d && docker logs -f fill



sync_from_host:
	rsync -av --progress  -r python/.layouteagle/ deploy@self-reading-library.science:/home/deploy/self-reading-library/python/.layouteagle/
sync_from_remote:
	rsync -av --progress  -r deploy@self-reading-library.science:/home/deploy/self-reading-library/python/.layouteagle/ python/.layouteagle/
