# JARVIS 2 — glass map

Two products. Do not merge them.

| Host | Job | Audience |
|---|---|---|
| **jarvis.lan** | The product. Life, briefings, conversation with JARVIS | Tony |
| **noc.lan** | True command center. Infra, logs, alerts | Operator when the house is sick |
| chat.lan, agent.lan, llm.lan, git.lan, grafana.lan | Break-glass / vendor UIs | You, when glass is dead |

home.lan (current Home + Status tabs) is retired. Collapse both into **noc.lan** and rebuild. Do not theme-skin the old homepage into jarvis.lan.

Palette on jarvis.lan only: #07090b, teal #5eead4, steel muted, IBM Plex Sans/Mono, hex mark.
noc.lan can share the palette but density and type are different (data first, not presence).

---

## 1. jarvis.lan — the product

Not a NOC. A quiet glass. Stage + Dock are the product. Infra is a pulse, not a wall.

```
┌──────────────────────────────────────────────────────────────┐
│  HEX   JARVIS                         voice ●    confirm (0) │
├──────────────────────────────────────────────┬───────────────┤
│                                              │               │
│                 STAGE                        │     DOCK      │
│         briefing · life · globe · forge      │  conversation │
│                                              │  pending yes  │
│                                              │               │
├──────────────────────────────────────────────┴───────────────┤
│  pulse   house ok · next: 14:00 school pickup · confirm 0    │
└──────────────────────────────────────────────────────────────┘
```

Default landing: **today’s briefing**, not node cards.

### Pulse (bottom, always on, tiny)

One line. Facts only, from telemetry + calendar — never from the 7B.

Examples: `house ok` · `inference cold` · `next: 14:00 pickup` · `confirm 1`

Clicking `house ok` / `inference cold` does **not** dump pods here. It deep-links to noc.lan.

### Stage panes (jarvis.lan)

**Briefing (default)**  
Morning / on-demand card: calendar next 3, remembered notes that matter today, one house sentence (“inference up, gpu-02 embed idle”). Mail is a count only; opening a message is confirm (`life.mail.read`).

**Life**  
Calendar, Telegram threads, X read, Docs drafts. Mail list after confirm. No node tables.

**Globe**  
`jarvis.lan/globe` — God’s Eye View pane. House pin later. No cameras v1.

**Forge**  
PRs and “I drafted a patch.” Propose is visible. Apply/merge still confirm. Keep this pane visually secondary so it does not turn Tony’s glass into Git.

**Memory**  
`learned.md` append, `briefing.md` read. Not a file manager.

No left rack rail on jarvis.lan. That belongs on noc.lan.

### Dock

The mouth. Voice and typed land here. Confirm cards land here (and as a modal over Stage if the verb is large).

Telegram can mirror Dock text. Confirm for send still exists.

---

## 2. noc.lan — the NOC

One surface. Replaces home.lan Home + Status.

This is the behind-the-scenes view: nodes, networks, services, apps, logs, alerts. Custom front end. Not Grafana-in-an-iframe as the product (Grafana stays break-glass for deep dashboards).

### Independence rule (non-negotiable)

noc.lan must still answer if **jarvis-core / Open WebUI / LiteLLM / Ollama / OpenClaw** are down.

That means:

- Separate Deployment + Service + Ingress from jarvis.lan
- Telemetry collector is **not** the orchestrator. Prefer Prometheus + a thin API on ctrl-01 or a static sidecar that can read node metrics even when apps-01 is sad
- TLS + DNS on the router, same as today
- No dependency on the 7B, the Dock, or policy.yaml to render
- Worst case: noc.lan shows last scrape + “collector stale” rather than a blank JARVIS error page

If the whole k3s apiserver is dead, noc.lan cannot be magic — bastion SSH is the last glass. Document that. Do not pretend a web NOC survives control-plane death.

### noc.lan density (v1)

- Nodes + roles (ctrl, gpu-chat, gpu-embed, data, apps)
- Workloads that matter: k3s, ingress, gitea, inference, agents, jarvis-core, noc itself
- NFS / disk
- GPU util
- Ingress / certs
- Recent k8s events + container logs (select a workload)
- Alert list (from Alertmanager or a file you already scrape)
- Link out to grafana.lan, git.lan — do not rebuild those

Collapsed by default into sections. Search + one “what is red” view.

---

## 3. Break-glass (leave ugly)

| Host | Why it exists |
|---|---|
| chat.lan | Open WebUI if Dock is dead |
| agent.lan:18789 | OpenClaw direct |
| llm.lan | LiteLLM |
| git.lan | Gitea origin |
| grafana.lan | Prom graphs |
| bastion SSH as `agent` | last resort |

Do not theme these. Do not add features. If you need a new break-glass later: `piper` admin, `ollama` host UI — same rule.

---

## Confirm modal (unchanged, plus two rules)

- Title = verb id (`recycle.deploy`, `life.mail.send`)
- Body = target, namespace, blast radius
- Actions = Confirm / Cancel
- Voice = “Confirm …” / “Cancel”
- Telegram send = inline buttons that hit the same policy, not a second yes-path
- Confirm state lives in orchestrator, so a yes on Telegram clears the HUD badge

Also: **timeout**. A pending confirm dies after N minutes and must be re-issued. No stale “yes” on a recycle from this morning.

## What jarvis.lan must never do

- Look like a NOC
- Show a model picker or resolved-model chip
- Put Prometheus into the 7B prompt
- Own routing (policy.yaml + orchestrator)
- Restyle instead of shipping a verb
- Embed noc.lan as a widget that takes half the Stage
- Fail closed into a white error because inference is down — pulse can say `house degraded` and Dock can still try cloud router

## What noc.lan must never do

- Require JARVIS to be healthy
- Become the place you chat with JARVIS
- Hide behind the same single replica as jarvis.lan
