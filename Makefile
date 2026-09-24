CLUSTER := platform-lab
IMAGE   := pacer
TAG     := dev

.PHONY: up down status reset build load test dev

up:
	kind create cluster --config cluster/kind-config.yaml
	kubectl cluster-info --context kind-$(CLUSTER)

down:
	kind delete cluster --name $(CLUSTER)

status:
	kubectl get nodes -o wide
	kubectl get pods -A

reset: down up

build:
	docker build -t $(IMAGE):$(TAG) .

load: build
	kind load docker-image $(IMAGE):$(TAG) --name $(CLUSTER)

test:
	python -m pytest tests -q

dev:
	uvicorn app.main:app --reload --port 8000
