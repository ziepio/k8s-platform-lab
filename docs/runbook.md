# Runbook

## Building everything from scratch

Add these entries to your hosts file first, on Windows and in WSL if you
use both:

```
127.0.0.1 pacer.localtest.me
127.0.0.1 grafana.localtest.me
```

Then:

```bash
make up
make ingress
make certmanager
make argocd
make argocd-app
make monitoring
```

About fifteen minutes if the images are already cached, longer the first
time.

## Checking that it works

```bash
kubectl get nodes
kubectl -n argocd get application pacer     # Synced / Healthy
kubectl -n pacer get pods,ingress,certificate
curl -k -I https://pacer.localtest.me
```

In Prometheus, Status then Targets should list a `pacer` target in state
UP. In Grafana, the `pacer` dashboard comes from a ConfigMap, so it is
still there after a restart.

## After a reboot

kind nodes do not start on their own when Docker restarts:

```bash
docker start $(kind get nodes --name platform-lab | tr '\n' ' ')
kubectl wait --for=condition=Ready nodes --all --timeout=180s
```

## Problems I ran into

### The site would not load

Four separate causes, one on top of another:

1. The DNS resolver returned nothing for `localtest.me`. Many resolvers
   refuse to answer with private addresses. A hosts file entry solved it.
2. The ingress controller Service showed `EXTERNAL-IP: <pending>`. That
   meant I had installed the generic manifest instead of the kind one.
   kind has no load balancer, so the kind manifest uses host ports.
3. The controller pod was running on a worker node. Only the control-plane
   node has ports 80 and 443 mapped out of Docker, so traffic never
   reached it.
4. The real cause: the Makefile pulled the manifest from the `main`
   branch, and the version there had no `ingress-ready` in its
   `nodeSelector`. Pinning the manifest version fixed it for good.

What I take from it: do not install from a moving reference. `main` and
`latest` mean "whatever is there today".

### ArgoCD would not install

`kubectl apply` stores a copy of the manifest in an annotation, and
annotations have a 256 kB limit. The ApplicationSet CRD is larger than
that, so the apply failed.

`--server-side` keeps the state on the API server instead of in an
annotation, so the limit does not apply. If a client-side attempt already
created part of the resources, the retry needs `--force-conflicts` once to
take ownership of the fields.

### GitHub Actions could not assume the AWS role

The error was `Not authorized to perform sts:AssumeRoleWithWebIdentity`,
which points at the role and its trust policy. I checked the trust policy,
the OIDC provider, the audience, the permissions boundary and the secret
with the role ARN. All of them were correct.

CloudTrail gave the answer. The `sub` claim that GitHub sends looks like
this:

```
repo:owner@53996597/k8s-platform-lab@1365532861:ref:refs/heads/main
```

The AWS documentation and most guides still show `repo:owner/repo:ref:...`
without the numbers. GitHub now adds the numeric account and repository
IDs, because a name can be released and taken by someone else while an ID
cannot. My condition used the old format, so it did not match and STS
refused the request.

Matching the full claim with the IDs is stricter than the documented form,
so I kept it.

What I take from it: when authentication fails and the configuration looks
correct, stop reading the configuration and look at what actually arrived.
CloudTrail is the only place that shows both sides of the exchange.

### The build cache could not be exported

`Cache export is not supported for the docker driver`. The default buildx
driver on a GitHub runner cannot export layer cache.
`docker/setup-buildx-action` creates a builder on the `docker-container`
driver, which can.

### Pods in CrashLoopBackOff after editing the code

I removed a docstring that was the only statement in a class body, which
left the class empty and broke the file. `make test` finds this in under a
second. `kubectl` takes much longer to tell you the same thing.

### Code changes not showing up in the cluster

The image tag had not changed, so Kubernetes had no reason to do anything.
Either run `kubectl rollout restart`, or use a tag that changes with the
code. CI does the second one, using the commit SHA.

## Commands worth remembering

```bash
kubectl -n pacer get endpoints pacer          # empty means nothing is ready
kubectl -n pacer describe pod <name> | tail -25
kubectl -n pacer logs <pod> --previous        # logs from the container that died
kubectl -n argocd describe application pacer | tail -30
kubectl -n ingress-nginx get pod -o wide      # which node is it on
docker port platform-lab-control-plane        # are 80 and 443 mapped
```
