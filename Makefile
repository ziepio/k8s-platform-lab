CLUSTER := platform-lab
IMAGE   := pacer
TAG     := dev

.PHONY: up down status reset build load test dev deploy undeploy app logs

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
	python3 -m pytest tests -q

dev:
	python3 -m uvicorn app.main:app --reload --port 8000

deploy:
	kubectl apply -f k8s/
	kubectl -n pacer rollout status deployment/pacer

undeploy:
	kubectl delete -f k8s/ --ignore-not-found

app:
	kubectl -n pacer port-forward svc/pacer 8080:80

logs:
	kubectl -n pacer logs -l app.kubernetes.io/name=pacer -f --tail=50

