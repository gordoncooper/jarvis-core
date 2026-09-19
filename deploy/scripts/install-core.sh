#!/usr/bin/env bash
# Build jarvis-core glass on apps-01 and import into k3s on apps-01.
# Run on bastion as agent.
set -euo pipefail

echo "== who =="
whoami
if [ "$(whoami)" != "agent" ]; then
  echo "FATAL: run as user agent (sudo su - agent)." >&2
  exit 1
fi

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
# shellcheck disable=SC1091
. "$ROOT/VERSION"
SRC="$ROOT/core"
BUILD_HOST="${BUILD_HOST:-apps-01}"
IMAGE="${IMAGE_CORE:-docker.io/library/jarvis-core:v0.2.0}"

echo "== pins =="
echo "ROOT=$ROOT IMAGE=$IMAGE BUILD=$BUILD_HOST"

ls -ld "$SRC/Dockerfile" "$SRC/glass/server.py" "$SRC/glass/index.html" || {
  echo "FATAL: missing core build context" >&2
  exit 1
}

ssh -n -o BatchMode=yes "$BUILD_HOST" \
  'sudo apt-get update -qq && sudo DEBIAN_FRONTEND=noninteractive apt-get install -y docker.io'

tar -C "$SRC" -czf /tmp/jarvis-core-src.tgz Dockerfile glass
scp -o BatchMode=yes /tmp/jarvis-core-src.tgz "$BUILD_HOST:/tmp/jarvis-core-src.tgz"

ssh -o BatchMode=yes "$BUILD_HOST" "sudo env IMAGE=$IMAGE bash -s" << 'EOF'
set -euo pipefail
rm -rf /tmp/jarvis-core-build
mkdir -p /tmp/jarvis-core-build
tar -C /tmp/jarvis-core-build -xzf /tmp/jarvis-core-src.tgz
cd /tmp/jarvis-core-build
docker build -t "$IMAGE" .
docker save "$IMAGE" | k3s ctr images import -
k3s ctr images ls | grep jarvis-core || true
rm -rf /tmp/jarvis-core-build /tmp/jarvis-core-src.tgz
EOF
rm -f /tmp/jarvis-core-src.tgz

kubectl apply -f "$ROOT/deploy/k8s/jarvis-core.yaml"
kubectl -n apps rollout status deploy/jarvis-core --timeout=120s || {
  kubectl -n apps describe deploy/jarvis-core | tail -40
  kubectl -n apps get po -l app=jarvis-core -o wide
  exit 1
}

kubectl -n apps get po,ing -l app=jarvis-core -o wide
curl -sk https://jarvis.lan/health || true
echo
echo "OK  $IMAGE on $BUILD_HOST"
