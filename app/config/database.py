from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config.settings import settings
from app.models.user import User
from app.models.token import Token
from app.models.instagram_account import InstagramAccount
from app.models.conversation import Conversation
from app.models.message import Message
import logging

logger = logging.getLogger(__name__)

client: AsyncIOMotorClient = None


async def connect_to_mongo():
    """Create database connection"""
    global client
    try:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        await init_beanie(
            database=client.get_default_database(),
            document_models=[User, Token, InstagramAccount, Conversation, Message]
        )
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        logger.info("Disconnected from MongoDB")

