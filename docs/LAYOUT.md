# JARVIS 2 — jarvis-core + jarvis-noc on k3s

Flux does not reconcile these apps.
k3s still runs them. Gitea still holds cluster YAML for everything else.
Brain + NOC ship as images you import, same pattern as today’s homepage image.

## Two apps, two failure domains

| App | Host | Node | Dies when | Must survive |
|---|---|---|---|---|
| **jarvis-core** | jarvis.lan | apps-01 | orchestrator / Dock / face | n/a — this *is* the product |
| **jarvis-noc** | noc.lan | **ctrl-01** | noc UI | inference, OWUI, OpenClaw, jarvis-core down |

noc on ctrl-01 is the point. apps-01 can burn; you still get a NOC if the apiserver and ingress on ctrl-01 live.

DNS (router, same as today):

```
jarvis.lan  →  192.168.8.11   # Traefik on ctrl-01, route to apps-01 Service
noc.lan     →  192.168.8.11   # Traefik on ctrl-01, route to noc on ctrl-01
```

home.lan stays a CNAME/redirect to noc.lan until you delete it.

## Repos

Do not dump this into jarvis-infra chrome or Flux `clusters/jarvis/apps`.

```
jarvis-core/                 # GitHub origin, like jarvis-infra
  policy.yaml                # the law (copy of artifacts/jarvis2-policy.yaml)
  orchestrator/              # verb router, confirm store, audit
  glass/                     # jarvis.lan frontend (Stage + Dock + pulse)
  workers/
    hands/                   # kubectl via SA, existing recycle Role
    memory/                  # learned.md + briefing.md
    life/                    # Google / Telegram / X adapters
    forge/                   # Gitea PRs
    eye/                     # globe embed config only
  deploy/
    k8s/jarvis-core.yaml     # Deployment, Service, Ingress, SA
    install.sh               # build + ctr import on apps-01 + kubectl apply
  docs/SPEC.md               # points at policy + hud-ia

jarvis-noc/                  # can live as a second top-level in same repo
  ui/                        # custom NOC frontend
  collector/                 # thin read API: nodes, pods, events, disk, gpu
  deploy/
    k8s/jarvis-noc.yaml      # pinned to ctrl-01
    install.sh
```

Same GitHub repo is fine if you hate repo sprawl:

```
gordoncooper/jarvis-core
  /core
  /noc
  /policy.yaml
```

Gitea is **not** the origin for this tree until you decide you want a LAN mirror. Flux never watches it.

## What still uses Flux / Gitea

Leave alone for now:

- k3s join, Traefik, certs, Gitea itself
- Ollama, LiteLLM, Open WebUI, Piper, OpenClaw, Prometheus, Grafana
- NFS, monitoring

Those are the house. jarvis-core *calls* them. It does not become them.

When you later want GitOps for the brain, that is a new conversation. Not v1.

## Images and install (match what you already do)

Same contract as `apps/jarvis-home`:

1. Build on apps-01 (or bastion, then import).
2. `k3s ctr images import`
3. `kubectl apply -f deploy/k8s/...` from **agent@bastion**
4. Pin names in a VERSION file inside **this** repo, not jarvis-infra/VERSION
5. Proof scripts: `curl -k https://jarvis.lan/health` and `curl -k https://noc.lan/health`

Do not `kubectl apply` from a laptop. Do not copy kubeconfig off-bastion.

## Kubernetes shape

### jarvis-core (apps-01)

```
Deployment jarvis-core
  replicas: 1
  nodeName / nodeSelector: apps-01
  containers:
    - glass        (static + SSR, :8080)
    - orchestrator (:8081)   # policy.yaml mounted
  volume: NFS or hostPath for learned.md + audit.jsonl
Service + Ingress host=jarvis.lan
SA jarvis-hands
  RoleBinding → existing openclaw-recycle
  extra Role: get nodes/pods/events (inspect.*)
```

Orchestrator talks to:

- LiteLLM `https://llm.lan/v1` (face / router / forge)
- OpenClaw only if you keep it as a Hands backend; target is to fold Hands into orchestrator and leave OpenClaw as break-glass
- Gitea API for forge.propose
- Google / Telegram / X via secrets in k8s Secret (SOPS later, USB keys now)

### jarvis-noc (ctrl-01)

```
Deployment jarvis-noc
  replicas: 1
  nodeName: ctrl-01
  containers:
    - ui         (:8080)
    - collector  (:8081)   # in-cluster kube API + node exporter / nvidia
Service + Ingress host=noc.lan
SA jarvis-noc
  Role: get/list/watch nodes, pods, deployments, events, logs
  NO delete, NO patch
```

collector does not import policy.yaml. It does not call LiteLLM.

If apps-01 is dead: jarvis.lan 502s. noc.lan still 200s.

If ctrl-01 is dead: both glass and cluster are in trouble. Bastion.

## Shared vs forbidden

**Share**

- mkcert / Traefik
- Prometheus as a *source* for noc collector (optional; kube API is enough for v1)
- briefing.md from git (read-only mount or fetch)
- palette tokens (CSS variables file)

**Do not share**

- one Deployment
- one SQLite
- one process that is both Dock and NOC
- Flux reconciliation
- 7B inside noc

## Cutover of home.lan

1. Ship noc.lan next to home.lan
2. Prove noc.lan with inference scaled to 0
3. Redirect home.lan → noc.lan
4. Delete old homepage image deploy when you are bored, not before

jarvis.lan can go live before home.lan dies. Parallel is good.

## First proof (before UI polish)

```
# from agent@bastion
kubectl -n jarvis get deploy,po,ing
curl -kI https://noc.lan/health
kubectl -n inference scale deploy <chat> --replicas=0
curl -kI https://noc.lan/health          # still 200
curl -kI https://jarvis.lan/health       # may 200 with pulse=degraded
kubectl -n inference scale deploy <chat> --replicas=1
```

If noc.lan dies when you scale inference, the independence rule failed. Fix that before any HUD CSS.

## What we explicitly do not build in this sitting

- Flux HelmRelease for these apps
- Replacing Ollama / LiteLLM
- Cameras
- HA devices
- God’s Eye as a rewrite (embed later)
