#!/usr/bin/env bash
# agent@bastion only. Builds on apps-01, imports on ctrl-01 (imagePullPolicy Never
# is node-local on k3s unless you import everywhere the pod can land).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# shellcheck disable=SC1091
source "$ROOT/VERSION"
IMAGE="${IMAGE_NOC:-docker.io/library/jarvis-noc:v0.1.0}"

if [[ "$(whoami)" != "agent" ]]; then
  echo "run as agent, not $(whoami)" >&2
  exit 1
fi

echo "build $IMAGE on apps-01"
ssh agent@192.168.8.16 "mkdir -p /tmp/jarvis-noc"
rsync -az --delete "$ROOT/noc/" "agent@192.168.8.16:/tmp/jarvis-noc/"
ssh agent@192.168.8.16 "sudo k3s ctr version >/dev/null 2>&1 || true; docker build -t $IMAGE /tmp/jarvis-noc && docker save $IMAGE | sudo k3s ctr images import -"

echo "import $IMAGE on ctrl-01 (pod lands here)"
ssh agent@192.168.8.11 "docker version >/dev/null 2>&1 && docker pull $IMAGE >/dev/null 2>&1 || true"
ssh agent@192.168.8.16 "docker save $IMAGE" | ssh agent@192.168.8.11 "sudo k3s ctr images import -"

echo "apply manifests"
kubectl apply -f "$ROOT/deploy/k8s/jarvis-noc.yaml"
kubectl -n apps rollout status deploy/jarvis-noc --timeout=90s
echo "proof:"
curl -skI https://noc.lan/health || curl -sk http://noc.lan/health || true
kubectl -n apps get po,ing -l app=jarvis-noc
