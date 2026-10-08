CLUSTER := platform-lab
IMAGE   := pacer
TAG     := dev

.PHONY: up down status reset build load test dev deploy undeploy app logs chart-lint chart-render chart-install chart-uninstall

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


# Helm
chart-lint:
	helm lint charts/pacer

chart-render:
	helm template pacer charts/pacer

chart-install:
	helm upgrade --install pacer charts/pacer \
		--namespace pacer --create-namespace --wait

chart-uninstall:
	helm uninstall pacer --namespace pacer


# ArgoCD
argocd:
	kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
	kubectl -n argocd rollout status deployment/argocd-server --timeout=300s

argocd-app:
	kubectl apply -f platform/argocd/application-pacer.yaml

argocd-pass:
	@kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo

argocd-ui:
	kubectl -n argocd port-forward svc/argocd-server 8443:443

