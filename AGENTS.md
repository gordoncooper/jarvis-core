# jarvis-core — prior art, read-only

**This repo is superseded (D-0003). Do not extend it.**

The contract is jarvis-infra
[AGENTS.md](https://github.com/gordoncooper/jarvis-infra/blob/main/AGENTS.md),
then [docs/DECISIONS.md](https://github.com/gordoncooper/jarvis-infra/blob/main/docs/DECISIONS.md).
A dated decision outranks any prose in this repo.

## Do not treat this repo's docs as law

- `policy.yaml` is **not enforced**. Nothing loads or parses it — no
  orchestrator, no worker, no manifest mount. A verb written there is neither
  permitted nor blocked at runtime. Read it as a proposal.
- `docs/HUD.md` and `docs/LAYOUT.md` describe a system that was mostly never
  built. LAYOUT references `workers/`, `artifacts/`, and `docs/SPEC.md` that do
  not exist, names the namespace `jarvis` when the manifests use `apps`, and
  describes two-container deployments that ship as one.
- Roughly 10–15% of the written design exists: the noc collector
  (`/health`, `/api/snapshot`) and a static glass stub with `/api/pulse`.

These are catalogued rather than fixed, because the repo is frozen.

Read-only here is a design rule, not a file lock: `deploy/scripts/install-*.sh`
still deploy the live `jarvis.lan` and `noc.lan`, so edits are not blocked and
git history is the undo. Do not build anything new here.

## Rules that still apply here

- You are on the bastion as `agent`. Use the shell; do not emit heredocs.
- This repo pushes to **GitHub**. Flux never watches it.
- `deploy/scripts/install-*.sh` are the one documented exception to the
  no-`kubectl apply` rule, precisely because Flux does not reconcile them.
  Everything Flux owns still goes through `~/cluster` and Gitea.
- No Vite, no App Builder, no kubeconfig on a laptop.
