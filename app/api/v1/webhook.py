from fastapi import APIRouter, Query, Request, status
from fastapi.responses import PlainTextResponse
from app.services import webhook_service
from app.config.settings import settings

router = APIRouter()


@router.get("")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
):
    """Webhook verification endpoint for Meta"""
    challenge = await webhook_service.verify_webhook(hub_mode, hub_verify_token, hub_challenge)
    if challenge:
        return PlainTextResponse(challenge)
    return PlainTextResponse("Forbidden", status_code=status.HTTP_403_FORBIDDEN)


@router.post("")
async def handle_webhook(request: Request):
    """Handle webhook events from Meta"""
    event_data = await request.json()
    result = await webhook_service.process_webhook_event(event_data)
    return result

