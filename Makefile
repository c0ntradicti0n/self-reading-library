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
	DOCKER_BUILDKIT=1 BUILDKIT_PROGRESS=plain docker-compose up -d

.PHONY: dockerdown
dockerdown:
	DOCKER_BUILDKIT=1 docker-compose down -v

.PHONY: backend
backend:
	cd python && python backend.py

.PHONY: frontend
frontend:
	cd react/layout_viewer_made/ && yarn run dev

