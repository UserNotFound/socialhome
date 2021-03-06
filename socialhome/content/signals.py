import json
import logging

import django_rq
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from socialhome.content.models import Content
from socialhome.content.previews import fetch_content_preview
from socialhome.enums import Visibility
from socialhome.federate.tasks import send_content, send_content_retraction
from socialhome.streams.consumers import StreamConsumer

logger = logging.getLogger("socialhome")


@receiver(post_save, sender=Content)
def notify_listeners(sender, **kwargs):
    if kwargs.get("created"):
        content = kwargs.get("instance")
        if content.visibility == Visibility.PUBLIC:
            StreamConsumer.group_send("streams_public", json.dumps({
                "event": "new",
                "id": content.id,
            }))


@receiver(post_save, sender=Content)
def federate_content(sender, **kwargs):
    """Send out local content to the federation layer.

    Yes, edits also. The federation layer should decide whether these are really worth sending out.
    """
    content = kwargs.get("instance")
    if content.is_local:
        try:
            django_rq.enqueue(send_content, content.id)
        except Exception as ex:
            logger.exception("Failed to federate_content %s: %s", content, ex)


@receiver(post_delete, sender=Content)
def federate_content_retraction(sender, **kwargs):
    """Send out local content retractions to the federation layer."""
    content = kwargs.get("instance")
    if content.is_local:
        try:
            django_rq.enqueue(send_content_retraction, content.id, content.author_id)
        except Exception as ex:
            logger.exception("Failed to federate_content_retraction %s: %s", content, ex)


@receiver(post_save, sender=Content)
def fetch_preview(instance, **kwargs):
    try:
        fetch_content_preview(instance)
    except Exception as ex:
        logger.exception("Failed to fetch content preview for %s: %s", instance, ex)
