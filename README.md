# jarvis-core — prior art

**Status: superseded. Read-only reference. Do not extend.**

Decided 2026-09-19 (D-0003 in
[jarvis-infra/docs/DECISIONS.md](https://github.com/gordoncooper/jarvis-infra/blob/main/docs/DECISIONS.md)):
this was the second attempt at the JARVIS brain, and the third attempt starts
clean rather than building on it. The contract that governs all work is
[jarvis-infra/AGENTS.md](https://github.com/gordoncooper/jarvis-infra/blob/main/AGENTS.md).

## Why it is kept

The thinking here was the best the project has produced. It is an input to the
next design, at the same rank as any other proposal — not a binding spec.

- `policy.yaml` — the verb model: every capability named, each with a
  `trusted` / `confirm` / `refuse` class, a worker, and a proof command. The
  principle that an undeclared verb is refused is worth carrying forward.
- `docs/HUD.md` — the split between a calm product surface and a dense NOC, and
  the rule that the NOC must render when the brain is down.
- `docs/LAYOUT.md` — deployment shape. Largely describes files that were never
  written; treat as a sketch, not a map.

## What is actually built

Roughly 10–15% of what the docs describe. Honest inventory:

| Piece | State |
| --- | --- |
| `noc/` collector — `/health`, `/api/snapshot` (nodes + pod counts) | works |
| `noc/ui/` node table | minimal |
| `core/glass/` static page + `/api/pulse` reading the noc snapshot | stub |
| `core/orchestrator/` | empty placeholder |
| Verb execution, confirm flow, audit log, workers | never written |
| NOC GPU / disk / events / logs / alerts | never written |

Nothing loads `policy.yaml`. No code parses it; no manifest mounts it. It is a
document, not an enforcement point — do not assume a verb is enforced because it
is written there.

Both apps are deployed outside Flux by `deploy/scripts/install-*.sh`, which is
the documented exception to the no-`kubectl apply` rule. They currently serve
`jarvis.lan` and `noc.lan`.

## If you are an AI reading this

Do not treat `policy.yaml` or `docs/HUD.md` as law, and do not build new
features here. Start at jarvis-infra `AGENTS.md`, then `docs/DECISIONS.md`.
Known-stale details in this repo's docs are catalogued rather than fixed,
because the repo is frozen: `docs/LAYOUT.md` references directories that do not
exist (`workers/`, `artifacts/`, `docs/SPEC.md`), names the namespace `jarvis`
when the manifests use `apps`, and describes two-container deployments that ship
as one.
