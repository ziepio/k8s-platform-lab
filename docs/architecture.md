# Architecture notes

Why the project is built this way, and what I would change before running
it with real traffic.

## How a change reaches the cluster

A commit on `main` starts the GitHub Actions workflow. Unit tests and a
Helm chart lint run first. Nothing is published unless both pass.

The publish job authenticates to AWS using OIDC. There is no access key in
this repository and none in its secrets. GitHub creates a short-lived token
that describes the workflow, AWS accepts it because the identity provider
is registered, and the trust policy limits it to this repository only.

The image is tagged with the short commit SHA. The workflow then updates
`image.tag` in `charts/pacer/values.yaml` and commits that change back to
the repository.

That commit is the handover point between CI and CD. The pipeline has no
cluster credentials and does not know that the cluster exists. ArgoCD sees
the new commit, renders the chart and applies it. CI pushes, CD pulls.

## Why these tools

**kind instead of minikube or k3d.** kind creates its nodes with kubeadm,
so what I learn here also applies to the CKA exam and to a real cluster.
k3s is a good tool, but it replaces several components with its own
versions, which makes it a slightly different system to learn.

**Three nodes instead of one.** A single node hides scheduling. With three
I can see pods land on different workers and watch what happens when one
node is stopped.

**Plain manifests before Helm.** Templating is easier to understand once
you know what it produces.

**Public ECR instead of a private registry.** A private registry needs a
pull secret with a token that expires every twelve hours. That is hard to
work with in a local lab. Public ECR lets kind pull the image without any
credentials, and still shows the AWS side of the setup.

**A self-signed CA instead of Let's Encrypt.** ACME needs a domain that
resolves publicly. The chain here has the same structure: root, CA, leaf.
Switching to a real issuer is a one-line change in the `ClusterIssuer`.

## What I would change for production

**Prometheus has no storage.** Metrics are lost when the pod restarts.
This is fine in a lab and useless anywhere else. The fix is a `storageSpec`
with a real `StorageClass`, plus remote write or Thanos if the data needs
to live longer than the node.

**Every platform component runs once.** ArgoCD, the ingress controller and
Prometheus all have a single replica. If one of them fails, that capability
is gone until it restarts.

**No PodDisruptionBudget on pacer.** It does not matter while nothing
drains the nodes. It would matter on managed infrastructure with rolling
node upgrades.

**No ResourceQuota or LimitRange on the namespace.** A single careless
manifest could use up the node's memory.

**Alertmanager sends alerts nowhere.** They fire and stay in the UI.
Connecting it to email or Slack is configuration work that I have not done.

**The Grafana admin password sits in a values file.** In a real cluster it
belongs in a Secret that never enters git: sealed-secrets, external-secrets
or a cloud secret store.

**ArgoCD tracks resources with the `app.kubernetes.io/instance` label**,
and the chart sets the same label. They agree here because the release name
and the Application name are both `pacer`. With different names they would
conflict. Switching ArgoCD to annotation-based tracking removes the risk.
