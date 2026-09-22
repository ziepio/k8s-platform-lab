CLUSTER := platform-lab

.PHONY: up down status reset

up:
	kind create cluster --config cluster/kind-config.yaml
	kubectl cluster-info --context kind-$(CLUSTER)

down:
	kind delete cluster --name $(CLUSTER)

status:
	kubectl get nodes -o wide
	kubectl get pods -A

reset: down up
