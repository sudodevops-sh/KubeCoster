# KubeCoster 💸

**Stop paying for Kubernetes resources nobody is using.**

KubeCoster is a lightweight Kubernetes operator that watches expensive resources — LoadBalancer services and PersistentVolumes — and automatically **notifies or deletes** them when they outlive their allowed age.

You define the rules. KubeCoster enforces them.

---

## What It Does

| Resource | What KubeCoster Does |
|---|---|
| `Service` (LoadBalancer) | Tracks creation time. Alerts or deletes when it exceeds your policy. |
| `PersistentVolume` | Cleans up orphaned (`Released`/`Available`) PVs past their allowed age. |

---

## Quick Start

### 1. Install the CRD + Operator

```bash
kubectl apply -f deploy/crds/costpolicy.yaml
kubectl apply -f deploy/rbac/cluster_role.yaml
kubectl apply -f deploy/operator.yaml
```

### 2. Define a Cost Policy

Create a `CostPolicy` to set the rules for your namespaces:

```yaml
apiVersion: frugalk8s.io/v1alpha1
kind: CostPolicy
metadata:
  name: my-cost-policy
spec:
  managedResources:
    - services
    - persistentvolumes
  maxAge: "24h"           # Max allowed lifetime
  action: notify          # "notify" to log, "delete" to auto-remove
  targetNamespaces:
    - dev
    - staging
```

```bash
kubectl apply -f my-cost-policy.yaml
```

That's it. KubeCoster will start enforcing the policy every 5 minutes.

---

## Deploy via Helm

```bash
helm install kubecoster ./charts/kubecoster \
  --namespace kubecoster --create-namespace \
  --set image.repository=<your-registry>/kubecoster \
  --set image.tag=<version>
```

---

## CostPolicy Options

| Field | Description | Example |
|---|---|---|
| `managedResources` | Which resource types to watch | `["services", "persistentvolumes"]` |
| `maxAge` | Maximum allowed age | `"24h"`, `"7d"` |
| `action` | What happens on violation | `"notify"` or `"delete"` |
| `targetNamespaces` | Namespaces this policy covers | `["dev", "staging"]` |

---

## Local Development

```bash
# Install dependencies (including dev tools)
uv sync --group dev

# Run the operator locally against your cluster
uv run kopf run cmd/main.py --verbose

# Lint
uv run task lint

# Test
uv run pytest tests/ -v
```

---

## Requirements

- Kubernetes **1.25+**
- Python **3.11+**
- Helm **3.x** *(for Helm install)*
