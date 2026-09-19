# jarvis-core

Greenfield JARVIS 2 brain + NOC. Flux does not watch this repo.

| Surface | App | Node |
|---|---|---|
| https://jarvis.lan | core (not in this slice) | apps-01 |
| https://noc.lan | noc | ctrl-01 |

Specs: `policy.yaml`, `docs/HUD.md`, `docs/LAYOUT.md`.

## This slice

noc.lan health + stub glass on **ctrl-01**.

Does not call LiteLLM, Open WebUI, Ollama, or jarvis-core.

## Install (agent@bastion)

```bash
sudo su - agent
cd ~/jarvis-core
. ./VERSION
./deploy/scripts/install-noc.sh
```

Router DNS: `noc.lan` → `192.168.8.11` (same as home.lan). TLS uses existing `lan-tls` in `apps`.

## Proof

```bash
curl -kI https://noc.lan/health
kubectl -n inference scale deploy --all --replicas=0   # or the chat deploy name
curl -kI https://noc.lan/health          # must still 200
```
