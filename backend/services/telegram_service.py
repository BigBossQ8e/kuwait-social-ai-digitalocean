"""
Telegram Service for Kuwait Social AI - Updated for v22.2
Handles Telegram integration for individual clients
"""
import os
import logging
from typing import Optional, List, Dict
import asyncio

# Updated imports for python-telegram-bot v22.2
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from models import db, Client, TelegramAccount, Post, PostApproval
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for handling Telegram operations for a specific client"""
    
    def __init__(self, client_id: int):
        self.client_id = client_id
        self.client = None
        self.telegram_account = None
        self.bot = None
        self.application = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the service with client data"""
        self.client = Client.query.get(self.client_id)
        if not self.client:
            raise ValueError(f"Client {self.client_id} not found")
        
        # Get telegram account
        self.telegram_account = TelegramAccount.query.filter_by(
            client_id=self.client_id
        ).first()
        
        if self.telegram_account and self.telegram_account.bot_token:
            self._setup_bot()
    
    def _setup_bot(self):
        """Setup the telegram bot"""
        try:
            self.bot = Bot(token=self.telegram_account.bot_token)
            self.application = Application.builder().token(self.telegram_account.bot_token).build()
            logger.info(f"Telegram bot setup for client {self.client_id}")
        except Exception as e:
            logger.error(f"Failed to setup Telegram bot: {e}")
            self.bot = None
            self.application = None
    
    async def send_notification(self, chat_id: str, message: str, parse_mode: str = None) -> bool:
        """Send a notification to a Telegram chat"""
        if not self.bot:
            logger.warning(f"No bot configured for client {self.client_id}")
            return False
        
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=parse_mode or ParseMode.MARKDOWN
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False
    
    async def send_post_for_approval(self, post: Post) -> bool:
        """Send a post for approval via Telegram"""
        if not self.telegram_account or not self.telegram_account.admin_chat_ids:
            logger.warning(f"No admin chat IDs configured for client {self.client_id}")
            return False
        
        # Format the post
        platform_emojis = {
            'instagram': '📷',
            'twitter': '🐦',
            'snapchat': '👻',
            'tiktok': '🎵',
            'youtube': '📺'
        }
        
        emoji = platform_emojis.get(post.platform.lower(), '📱')
        content_preview = post.content[:200] + "..." if len(post.content) > 200 else post.content
        
        message = (
            f"{emoji} *New {post.platform} Post*\n"
            f"━━━━━━━━━━━━━\n\n"
            f"{content_preview}\n\n"
            f"*Scheduled:* {post.scheduled_time.strftime('%b %d, %H:%M') if post.scheduled_time else 'Not scheduled'}\n"
            f"*ID:* #{post.id}"
        )
        
        # Create approval buttons
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{post.id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{post.id}")
            ]
        ])
        
        # Send to all admin chats
        success = False
        for chat_id in self.telegram_account.admin_chat_ids:
            try:
                msg = await self.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=keyboard
                )
                
                # Store message ID for tracking
                approval = PostApproval.query.filter_by(post_id=post.id).first()
                if not approval:
                    approval = PostApproval(post_id=post.id)
                approval.telegram_message_id = str(msg.message_id)
                approval.status = 'pending'
                db.session.add(approval)
                
                success = True
            except Exception as e:
                logger.error(f"Failed to send to chat {chat_id}: {e}")
        
        if success:
            db.session.commit()
        
        return success
    
    def validate_bot_token(self, token: str) -> Dict[str, any]:
        """Validate a bot token"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            bot = Bot(token=token)
            bot_info = loop.run_until_complete(bot.get_me())
            return {
                'valid': True,
                'username': bot_info.username,
                'name': bot_info.first_name,
                'id': bot_info.id
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def setup_webhook(self, webhook_url: str) -> bool:
        """Setup webhook for the bot"""
        if not self.bot:
            return False
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.bot.set_webhook(webhook_url))
            return True
        except Exception as e:
            logger.error(f"Failed to setup webhook: {e}")
            return False


# Singleton instance management
_telegram_services = {}

def get_telegram_service(client_id: int = None) -> TelegramService:
    """Get or create a TelegramService instance for a client"""
    if client_id is None:
        # Return a dummy service if no client_id provided
        # This is for backward compatibility
        return TelegramService(1)  # Use a default client ID
    
    global _telegram_services
    if client_id not in _telegram_services:
        _telegram_services[client_id] = TelegramService(client_id)
    return _telegram_services[client_id]


# Singleton instance
_telegram_service = None

def get_telegram_service():
    """Get or create the singleton TelegramService instance"""
    global _telegram_service
    if _telegram_service is None:
        _telegram_service = TelegramService()
    return _telegram_service
