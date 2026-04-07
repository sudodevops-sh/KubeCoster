import kopf
import logging
import internal.controller.lb_handler

@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, logger, **kwargs):
    logger.info(f"🚀 KubeCoster starting up...")
    settings.scanning.cluster_managed = True
    settings.execution.max_workers = 10
    settings.peering.standalone = True