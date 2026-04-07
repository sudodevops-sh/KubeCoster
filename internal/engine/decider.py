import datetime
from internal.k8s.utils import parse_duration

def should_action_resource(creation_timestamp, policy_spec):
    """
    Returns (bool, current_age_seconds)
    Central logic to determine if a resource has exceeded its TTL.
    """
    # Parse timestamps
    created_at = datetime.datetime.strptime(
        creation_timestamp, "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=datetime.timezone.utc)
    now = datetime.datetime.now(datetime.timezone.utc)
    age_seconds = (now - created_at).total_seconds()

    # compare againts policy
    max_age_seconds = parse_duration(policy_spec.get("maxAge", "24h"))
    return age_seconds > max_age_seconds, age_seconds