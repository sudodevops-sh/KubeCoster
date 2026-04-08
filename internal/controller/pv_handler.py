import kopf
import kubernetes
from internal.engine.decider import should_action_resource

@kopf.on.timer('persistentvolumes', interval=300)
def check_pv_expiry(name, body, logger, **kwargs):
    api = kubernetes.client.CustomObjectsApi()
    storage_api = kubernetes.client.CoreV1Api()
    
    # 1. Get Global Policies (PVs are cluster-scoped, not namespaced)
    policies = api.list_cluster_custom_object("frugalk8s.io", "v1alpha1", "costpolicies")
    
    # Check if any policy manages 'persistentvolumes'
    for policy in policies.get('items', []):
        spec = policy['spec']
        if 'persistentvolumes' not in spec.get('managedResources', []):
            continue

        # 2. Logic: Only action if the PV is NOT currently 'Bound'
        # A 'Released' or 'Available' PV is costing money without being used.
        phase = body.get('status', {}).get('phase')
        if phase in ['Released', 'Available']:
            
            is_expired, age = should_action_resource(
                body['metadata']['creationTimestamp'], 
                spec
            )
            
            if is_expired:
                action = spec.get('action', 'notify')
                if action == 'delete':
                    logger.warning(f"Deleting orphaned PV {name} (Age: {age}s, Phase: {phase})")
                    storage_api.delete_persistent_volume(name=name)
                else:
                    logger.info(f"Notification: PV {name} is orphaned and over-age.")