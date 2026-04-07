import kopf
import logging
import kubernetes
import datetime

from internal.k8s.utils import parse_duration

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger()

@kopf.on.create("services", when=lambda spec, **_: spec.get("type") == "LoadBalancer")
def monitor_svc_loadbalancer(name, namespace, patch, **kwargs):
    logger.info(f"New Loadbalancer type service detected: {name} in namespace {namespace}")
    # check if the service already has custom tracking annotation
    if "kubecoster.io/tracked" not in kwargs.get("annotations", {}):
        logger.info(f"Tagging {name} for cost tracking..")
        # Patch service to add annotation
        patch.metadata.annotations['kubecoster.io/tracked'] = 'true'
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        patch.metadata.annotations['kubecoster.io/discovery-time'] = now
    return None

@kopf.on.timer("services", interval=300, when=lambda spec, **_: spec.get("type") == "LoadBalancer")
def check_loadbalancer_expiry(name, namespace, body, **kwargs):
    api = kubernetes.client.CustomObjectsApi()
    core_api = kubernetes.client.CoreV1Api()

    # Fetch all CostPolicies in the cluster
    policies = api.list_cluster_custom_object(
        group="frugalk8s.io",
        version="v1alpha1",
        plural="costpolicies"
    )

    # Find the policy that applies to this namespace
    active_policy = None
    for policy in policies.get("items", []):
        if namespace in policy["spec"].get("targetNamespaces", []):
            active_policy = policy
            break
    
    if not active_policy:
        logger.debug(f"No CostPolicy found for namespace {namespace}. Skipping.")
        return
    
    # calculate age
    creation_timestamp = body["metadata"]["creationTimestamp"]
    created_at = datetime.datetime.strptime(
        creation_timestamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc
    )
    now = datetime.datetime.now(datetime.timezone.utc)
    age_seconds = (now - created_at).total_seconds()

    # compare with policy
    max_age_str = active_policy["spec"]["maxAge"]
    max_age_seconds = parse_duration(max_age_str)
    if age_seconds > max_age_seconds:
        action = active_policy["spec"].get("action", "notify")
        if action == "delete":
            logger.warning(f"❌ LB {name} expired ({age_seconds}s > {max_age_seconds}s). DELETING.")
            core_api.delete_namespaced_service(name=name, namespace=namespace)
        else:
            logger.info(f"⚠️ LB {name} is over budget age. Action is 'notify' only.")