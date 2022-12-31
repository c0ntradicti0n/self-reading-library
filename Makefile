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
	ENV=prod USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 docker-compose build
dev:
	ENV=dev USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 docker-compose build
build:
	USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 docker-compose build
build_fe:
	USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 docker-compose build fe
over:
	ENV=prod USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 docker-compose -f docker-compose.override.yaml  build
overup:
	ENV=prod USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 docker-compose -f docker-compose.override.yaml  up --build
overdown:
	ENV=prod USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 docker-compose -f docker-compose.override.yaml down || exit 0

CWD=$(shell pdw)
scrape_test:
	ENV=prod USER=$$USER CWD=$(shell pwd) DOCKER_BUILDKIT=1 docker run -v "$(shell pwd)/python:/home/finn/Programming/self-reading-library/python" full_python python3 core/standard_converter/Scraper.py


up:
	USER=$$USER CWD=$(shell pwd) UID="$(shell id -u)" GID="$(shell id -g)" DOCKER_BUILDKIT=1 docker-compose up -d  --build
down:
	CWD=$(shell pwd) DOCKER_BUILDKIT=1 docker-compose down

dockerlogs:
	docker logs -f rest
dockerdebug:
	docker exec -itd rest /usr/sbin/sshd -D
dbash:
	docker exec -it rest bash

d: down dockerbuild up

db:
	CWD=$(shell pwd) UID="$(shell id -u)" GID="$(shell id -g)" DOCKER_BUILDKIT=1 docker-compose  -f docker-compose.db.yml up -d gdb
dbdown:
	CWD=$(shell pwd) UID="$(shell id -u)" GID="$(shell id -g)" DOCKER_BUILDKIT=1 docker-compose  -f docker-compose.db.yml down -v

fe:
	cd react/layout_viewer_made/ && yarn run dev


docker-fill:
	docker-compose build fill && docker-compose up fill -d && docker logs -f fill

logs:
	docker-compose logs -f -t


sync_from_host:
	rsync -av --progress  -r python/.layouteagle/ deploy@self-reading-library.science:/home/deploy/self-reading-library/python/.layouteagle/
sync_from_remote:
	rsync -av --progress  -r deploy@self-reading-library.science:/home/deploy/self-reading-library/python/.layouteagle/ python/.layouteagle/

fresh: down dbdown db build up