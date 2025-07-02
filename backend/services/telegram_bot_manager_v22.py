"""
Telegram Bot Manager for Kuwait Social AI - Updated for v22.2
Manages multiple client-specific Telegram bots using async API
"""
import os
import logging
from typing import Dict, Optional
import asyncio
from datetime import datetime, timedelta

# Updated imports for python-telegram-bot v22.2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.constants import ParseMode
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters,
    CallbackQueryHandler, 
    ContextTypes
)

from models import db, TelegramAccount, Post, PostApproval, Client, TelegramCommand

logger = logging.getLogger(__name__)


class ClientTelegramBot:
    """Individual Telegram bot instance for a client"""
    
    def __init__(self, client_id: int, bot_token: str, bot_username: str):
        self.client_id = client_id
        self.bot_token = bot_token
        self.bot_username = bot_username
        self.bot = Bot(token=bot_token)
        self.application = None
        self._is_running = False
        
        try:
            # Create application with token
            self.application = Application.builder().token(bot_token).build()
            self._setup_handlers()
            logger.info(f"Initialized bot for client {client_id}: {bot_username}")
        except Exception as e:
            logger.error(f"Failed to initialize bot for client {client_id}: {e}")
            raise
    
    def _setup_handlers(self):
        """Setup bot command handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.handle_start))
        self.application.add_handler(CommandHandler("help", self.handle_help))
        self.application.add_handler(CommandHandler("pending", self.handle_pending))
        self.application.add_handler(CommandHandler("stats", self.handle_stats))
        self.application.add_handler(CommandHandler("settings", self.handle_settings))
        
        # Callback query handler for inline buttons
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Message handler
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self):
        """Start the bot"""
        if not self._is_running:
            self._is_running = True
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            logger.info(f"Started polling for client {self.client_id}")
    
    async def stop(self):
        """Stop the bot"""
        if self._is_running:
            self._is_running = False
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info(f"Stopped bot for client {self.client_id}")
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        # Check if this user is authorized for this client
        account = TelegramAccount.query.filter_by(
            client_id=self.client_id,
            chat_id=str(chat_id)
        ).first()
        
        if account and account.is_verified:
            client = Client.query.get(self.client_id)
            await update.message.reply_text(
                f"Welcome back to {client.company_name} Bot! 👋\n\n"
                "Your account is linked and ready.\n\n"
                "Commands:\n"
                "/pending - View posts awaiting approval\n"
                "/stats - View your statistics\n"
                "/settings - Manage preferences\n"
                "/help - Show all commands"
            )
        else:
            await update.message.reply_text(
                f"Welcome! 🚀\n\n"
                "This bot manages social media for a specific business.\n"
                "Please contact your administrator to link your account.\n\n"
                f"Your Chat ID: `{chat_id}`\n"
                "(Share this with your admin)",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def handle_pending(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pending command"""
        chat_id = update.effective_chat.id
        
        # Verify user is authorized
        account = TelegramAccount.query.filter_by(
            client_id=self.client_id,
            chat_id=str(chat_id),
            is_verified=True
        ).first()
        
        if not account:
            await update.message.reply_text("❌ Unauthorized. Please contact your administrator.")
            return
        
        # Get pending posts
        pending_posts = Post.query.join(PostApproval).filter(
            Post.client_id == self.client_id,
            PostApproval.status == 'pending'
        ).order_by(Post.scheduled_time).limit(5).all()
        
        if not pending_posts:
            await update.message.reply_text("✨ No posts pending approval!")
            return
        
        await update.message.reply_text(f"📋 {len(pending_posts)} posts awaiting approval:")
        
        for post in pending_posts:
            await self.send_post_for_approval(chat_id, post)
    
    async def handle_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        chat_id = update.effective_chat.id
        
        # Verify user
        account = TelegramAccount.query.filter_by(
            client_id=self.client_id,
            chat_id=str(chat_id),
            is_verified=True
        ).first()
        
        if not account:
            await update.message.reply_text("❌ Unauthorized.")
            return
        
        client = Client.query.get(self.client_id)
        
        # Calculate stats
        total_posts = Post.query.filter_by(client_id=self.client_id, status='published').count()
        posts_this_month = Post.query.filter(
            Post.client_id == self.client_id,
            Post.status == 'published',
            Post.published_time >= datetime.utcnow().replace(day=1)
        ).count()
        
        stats_text = (
            f"📊 *{client.company_name} Statistics*\n\n"
            f"*Posts:*\n"
            f"• Total Published: {total_posts}\n"
            f"• This Month: {posts_this_month}/{client.monthly_posts_limit}\n\n"
            f"*AI Credits:*\n"
            f"• Used: {client.ai_credits_used}/{client.ai_credits_limit}\n\n"
            f"*Plan:* {client.subscription_plan.title()}"
        )
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            f"🤖 *{self.bot_username} Commands*\n\n"
            "/start - Start the bot\n"
            "/pending - View posts awaiting approval\n"
            "/stats - View statistics\n"
            "/settings - Manage preferences\n"
            "/help - Show this message\n\n"
            "Use the inline buttons to approve or reject posts!"
        )
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command"""
        chat_id = update.effective_chat.id
        
        account = TelegramAccount.query.filter_by(
            client_id=self.client_id,
            chat_id=str(chat_id),
            is_verified=True
        ).first()
        
        if not account:
            await update.message.reply_text("❌ Unauthorized.")
            return
        
        keyboard = [
            [InlineKeyboardButton(
                f"{'✅' if account.notify_posts else '❌'} Post Notifications",
                callback_data="toggle_posts"
            )],
            [InlineKeyboardButton(
                f"{'✅' if account.notify_analytics else '❌'} Analytics",
                callback_data="toggle_analytics"
            )],
            [InlineKeyboardButton(
                f"Language: {'🇬🇧' if account.language_preference == 'en' else '🇰🇼'}",
                callback_data="toggle_language"
            )]
        ]
        
        await update.message.reply_text(
            "⚙️ *Settings*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        chat_id = query.message.chat_id
        
        # Get account
        account = TelegramAccount.query.filter_by(
            client_id=self.client_id,
            chat_id=str(chat_id)
        ).first()
        
        if not account:
            await query.edit_message_text("❌ Session expired.")
            return
        
        # Handle callbacks
        if data.startswith("approve_"):
            post_id = int(data.replace("approve_", ""))
            await self._approve_post(query, post_id)
        elif data.startswith("reject_"):
            post_id = int(data.replace("reject_", ""))
            await self._reject_post(query, post_id)
        elif data.startswith("manual_"):
            post_id = int(data.replace("manual_", ""))
            await self._send_manual_package(query, post_id)
        elif data.startswith("toggle_"):
            await self._toggle_setting(query, data, account)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        await update.message.reply_text(
            "Please use the available commands. Type /help for more info."
        )
    
    async def send_post_for_approval(self, chat_id: str, post: Post):
        """Send a post for approval"""
        try:
            # Format preview
            preview = self._format_post_preview(post)
            
            # Create keyboard
            keyboard = [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{post.id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{post.id}")
                ],
                [InlineKeyboardButton("📤 Manual Post", callback_data=f"manual_{post.id}")]
            ]
            
            # Send message
            message = await self.bot.send_message(
                chat_id=chat_id,
                text=preview,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
            # Update approval record
            approval = PostApproval.query.filter_by(post_id=post.id).first()
            if not approval:
                approval = PostApproval(post_id=post.id)
            
            approval.telegram_message_id = str(message.message_id)
            approval.status = 'pending'
            
            db.session.add(approval)
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send post for approval: {e}")
            return False
    
    def _format_post_preview(self, post: Post) -> str:
        """Format post for preview"""
        platform_emojis = {
            'instagram': '📷',
            'twitter': '🐦',
            'snapchat': '👻'
        }
        
        emoji = platform_emojis.get(post.platform.lower(), '📱')
        scheduled = post.scheduled_time.strftime("%b %d, %H:%M") if post.scheduled_time else "Not scheduled"
        
        content = post.content[:300] + "..." if len(post.content) > 300 else post.content
        hashtags = " ".join(post.hashtags[:5]) if post.hashtags else ""
        
        preview = (
            f"{emoji} *{post.platform} Post*\n"
            f"━━━━━━━━━━━━━\n\n"
            f"{content}\n\n"
            f"*Tags:* {hashtags}\n"
            f"*Schedule:* {scheduled}\n"
            f"*ID:* #{post.id}"
        )
        
        return preview
    
    async def _approve_post(self, query, post_id: int):
        """Approve a post"""
        post = Post.query.filter_by(id=post_id, client_id=self.client_id).first()
        if not post:
            await query.edit_message_text("❌ Post not found.")
            return
        
        approval = PostApproval.query.filter_by(post_id=post_id).first()
        if approval:
            approval.approve(via='telegram')
        
        post.status = 'approved'
        db.session.commit()
        
        await query.edit_message_text(f"✅ Post #{post_id} approved!")
    
    async def _reject_post(self, query, post_id: int):
        """Reject a post"""
        post = Post.query.filter_by(id=post_id, client_id=self.client_id).first()
        if not post:
            await query.edit_message_text("❌ Post not found.")
            return
        
        approval = PostApproval.query.filter_by(post_id=post_id).first()
        if approval:
            approval.reject(reason="Rejected via Telegram")
        
        post.status = 'rejected'
        db.session.commit()
        
        await query.edit_message_text(f"❌ Post #{post_id} rejected.")
    
    async def _send_manual_package(self, query, post_id: int):
        """Send manual posting package"""
        post = Post.query.filter_by(id=post_id, client_id=self.client_id).first()
        if not post:
            await query.edit_message_text("❌ Post not found.")
            return
        
        instructions = (
            f"📤 *Manual Posting*\n\n"
            f"*Caption:*\n```\n{post.content}\n```\n\n"
        )
        
        if post.hashtags:
            instructions += f"*Hashtags:*\n```\n{' '.join(post.hashtags)}\n```\n\n"
        
        instructions += "Copy and paste to your social media!"
        
        await query.edit_message_text(instructions, parse_mode=ParseMode.MARKDOWN)
    
    async def _toggle_setting(self, query, setting: str, account: TelegramAccount):
        """Toggle settings"""
        if setting == "toggle_posts":
            account.notify_posts = not account.notify_posts
        elif setting == "toggle_analytics":
            account.notify_analytics = not account.notify_analytics
        elif setting == "toggle_language":
            account.language_preference = 'ar' if account.language_preference == 'en' else 'en'
        
        db.session.commit()
        
        # Re-render settings with updated state
        keyboard = [
            [InlineKeyboardButton(
                f"{'✅' if account.notify_posts else '❌'} Post Notifications",
                callback_data="toggle_posts"
            )],
            [InlineKeyboardButton(
                f"{'✅' if account.notify_analytics else '❌'} Analytics",
                callback_data="toggle_analytics"
            )],
            [InlineKeyboardButton(
                f"Language: {'🇬🇧' if account.language_preference == 'en' else '🇰🇼'}",
                callback_data="toggle_language"
            )]
        ]
        
        await query.edit_message_text(
            "⚙️ *Settings*",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )


class TelegramBotManager:
    """Manages multiple client Telegram bots"""
    
    def __init__(self):
        self.bots: Dict[int, ClientTelegramBot] = {}
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        logger.info("Initialized Telegram Bot Manager")
    
    async def add_bot_async(self, client_id: int, bot_token: str, bot_username: str) -> bool:
        """Add a new client bot (async)"""
        try:
            # Stop existing bot if any
            if client_id in self.bots:
                await self.remove_bot_async(client_id)
            
            # Create new bot
            bot = ClientTelegramBot(client_id, bot_token, bot_username)
            self.bots[client_id] = bot
            
            # Start the bot
            await bot.start()
            
            logger.info(f"Added bot for client {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add bot for client {client_id}: {e}")
            return False
    
    def add_bot(self, client_id: int, bot_token: str, bot_username: str) -> bool:
        """Add a new client bot (sync wrapper)"""
        return self.loop.run_until_complete(
            self.add_bot_async(client_id, bot_token, bot_username)
        )
    
    async def remove_bot_async(self, client_id: int) -> bool:
        """Remove a client bot (async)"""
        if client_id in self.bots:
            try:
                await self.bots[client_id].stop()
                del self.bots[client_id]
                logger.info(f"Removed bot for client {client_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to remove bot for client {client_id}: {e}")
                return False
        return False
    
    def remove_bot(self, client_id: int) -> bool:
        """Remove a client bot (sync wrapper)"""
        return self.loop.run_until_complete(
            self.remove_bot_async(client_id)
        )
    
    def get_bot(self, client_id: int) -> Optional[ClientTelegramBot]:
        """Get a specific client bot"""
        return self.bots.get(client_id)
    
    async def validate_bot_token_async(self, token: str) -> Dict[str, any]:
        """Validate a bot token and get bot info (async)"""
        try:
            bot = Bot(token=token)
            bot_info = await bot.get_me()
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
    
    def validate_bot_token(self, token: str) -> Dict[str, any]:
        """Validate a bot token and get bot info (sync wrapper)"""
        return self.loop.run_until_complete(
            self.validate_bot_token_async(token)
        )
    
    async def initialize_from_database_async(self):
        """Initialize all bots from database on startup (async)"""
        try:
            # Get all active telegram accounts with bot tokens
            accounts = TelegramAccount.query.filter(
                TelegramAccount.bot_token.isnot(None),
                TelegramAccount.is_bot_active == True
            ).all()
            
            for account in accounts:
                if account.bot_token and account.client_id:
                    await self.add_bot_async(
                        account.client_id,
                        account.bot_token,
                        account.bot_username or f"bot_{account.client_id}"
                    )
            
            logger.info(f"Initialized {len(self.bots)} bots from database")
            
        except Exception as e:
            logger.error(f"Failed to initialize bots from database: {e}")
    
    def initialize_from_database(self):
        """Initialize all bots from database on startup (sync wrapper)"""
        self.loop.run_until_complete(
            self.initialize_from_database_async()
        )
    
    async def stop_all_async(self):
        """Stop all bots (async)"""
        for client_id in list(self.bots.keys()):
            await self.remove_bot_async(client_id)
        logger.info("Stopped all bots")
    
    def stop_all(self):
        """Stop all bots (sync wrapper)"""
        self.loop.run_until_complete(self.stop_all_async())


# Global bot manager instance
bot_manager = TelegramBotManager()


def get_bot_manager() -> TelegramBotManager:
    """Get the global bot manager instance"""
    return bot_manager