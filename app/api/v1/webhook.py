from fastapi import APIRouter, Query, Request, status
from fastapi.responses import PlainTextResponse
from app.services import webhook_service
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
):
    """Webhook verification endpoint for Meta"""
    logger.info(f"Webhook verification request: mode={hub_mode}, token_match={hub_verify_token == settings.META_VERIFY_TOKEN}")
    challenge = await webhook_service.verify_webhook(hub_mode, hub_verify_token, hub_challenge)
    if challenge:
        logger.info("Webhook verification successful")
        return PlainTextResponse(challenge)
    logger.warning("Webhook verification failed")
    return PlainTextResponse("Forbidden", status_code=status.HTTP_403_FORBIDDEN)


@router.post("")
async def handle_webhook(request: Request):
    """Handle webhook events from Meta"""
    try:
        event_data = await request.json()
        logger.info(f"Webhook POST received from {request.client.host if request.client else 'unknown'}")
        result = await webhook_service.process_webhook_event(event_data)
        return result
    except Exception as e:
        logger.error(f"Error handling webhook request: {e}", exc_info=True)
        return "EVENT_RECEIVED"  # Always return success to Meta

