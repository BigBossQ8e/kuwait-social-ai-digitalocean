"""
Telegram Bot Service for Kuwait Social AI
Handles bot integration, authentication, and post approval workflow
"""
import os
import logging
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from flask import current_app
from sqlalchemy.orm import Session

from models import db, TelegramAccount, Post, PostApproval, Client, TelegramCommand
from services.ai_service import AIService

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for managing Telegram bot interactions"""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize Telegram bot service"""
        self.token = token or os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            logger.warning("No Telegram bot token configured")
            self.bot = None
            self.updater = None
        else:
            try:
                self.bot = telegram.Bot(token=self.token)
                self.updater = Updater(token=self.token, use_context=True)
                self._setup_handlers()
                logger.info("Telegram bot initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
                self.bot = None
                self.updater = None
    
    def _setup_handlers(self):
        """Setup bot command handlers"""
        if not self.updater:
            return
        
        dispatcher = self.updater.dispatcher
        
        # Command handlers
        dispatcher.add_handler(CommandHandler("start", self.handle_start))
        dispatcher.add_handler(CommandHandler("link", self.handle_link))
        dispatcher.add_handler(CommandHandler("unlink", self.handle_unlink))
        dispatcher.add_handler(CommandHandler("pending", self.handle_pending))
        dispatcher.add_handler(CommandHandler("stats", self.handle_stats))
        dispatcher.add_handler(CommandHandler("help", self.handle_help))
        dispatcher.add_handler(CommandHandler("settings", self.handle_settings))
        
        # Callback query handler for inline buttons
        dispatcher.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Message handler for verification codes
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))
    
    def start_polling(self):
        """Start the bot polling"""
        if self.updater:
            self.updater.start_polling()
            logger.info("Telegram bot polling started")
    
    def stop(self):
        """Stop the bot"""
        if self.updater:
            self.updater.stop()
            logger.info("Telegram bot stopped")
    
    def generate_verification_code(self) -> str:
        """Generate a random verification code"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    async def handle_start(self, update: Update, context: CallbackContext):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        # Log command
        self._log_command(chat_id, "start")
        
        # Check if already linked
        account = TelegramAccount.query.filter_by(chat_id=str(chat_id)).first()
        
        if account and account.is_verified:
            await update.message.reply_text(
                f"Welcome back {user.first_name}! 👋\n\n"
                "Your account is already linked. Here's what you can do:\n\n"
                "/pending - View posts awaiting approval\n"
                "/stats - View your performance stats\n"
                "/settings - Manage notification preferences\n"
                "/help - Show all available commands"
            )
        else:
            await update.message.reply_text(
                f"Welcome to Kuwait Social AI Bot! 🚀\n\n"
                "I'll help you manage your social media posts with:\n"
                "✅ Post approvals\n"
                "📊 Performance analytics\n"
                "🔔 Real-time notifications\n\n"
                "To get started, please link your account:\n"
                "1. Go to your dashboard settings\n"
                "2. Click 'Link Telegram'\n"
                "3. Enter this code: /link <verification_code>\n\n"
                "Need help? Type /help"
            )
    
    async def handle_link(self, update: Update, context: CallbackContext):
        """Handle /link command for account linking"""
        chat_id = update.effective_chat.id
        user = update.effective_user
        
        # Log command
        self._log_command(chat_id, "link", " ".join(context.args))
        
        # Check if already linked
        existing = TelegramAccount.query.filter_by(chat_id=str(chat_id)).first()
        if existing and existing.is_verified:
            await update.message.reply_text(
                "❌ This Telegram account is already linked!\n"
                "Use /unlink to disconnect first."
            )
            return
        
        # Check for verification code
        if not context.args:
            await update.message.reply_text(
                "Please provide your verification code:\n"
                "/link YOUR_CODE\n\n"
                "Get your code from the dashboard settings."
            )
            return
        
        verification_code = context.args[0].upper()
        
        # Find account with this verification code
        account = TelegramAccount.query.filter_by(
            verification_code=verification_code,
            is_verified=False
        ).first()
        
        if not account:
            await update.message.reply_text(
                "❌ Invalid or expired verification code.\n"
                "Please get a new code from your dashboard."
            )
            return
        
        # Check if code is expired (valid for 10 minutes)
        if account.verification_expires and account.verification_expires < datetime.utcnow():
            await update.message.reply_text(
                "❌ This verification code has expired.\n"
                "Please generate a new one from your dashboard."
            )
            return
        
        # Update account with Telegram info
        account.chat_id = str(chat_id)
        account.telegram_id = str(user.id)
        account.telegram_username = user.username
        account.first_name = user.first_name
        account.last_name = user.last_name
        account.is_verified = True
        account.verification_code = None
        account.verification_expires = None
        account.linked_at = datetime.utcnow()
        
        db.session.commit()
        
        # Get client info
        client = Client.query.filter_by(id=account.client_id).first()
        company_name = client.company_name if client else "your account"
        
        await update.message.reply_text(
            f"✅ Success! Your Telegram is now linked to {company_name}.\n\n"
            "You'll receive notifications for:\n"
            "• Posts awaiting approval\n"
            "• Performance updates\n"
            "• Important alerts\n\n"
            "Type /help to see available commands."
        )
    
    async def handle_unlink(self, update: Update, context: CallbackContext):
        """Handle /unlink command"""
        chat_id = update.effective_chat.id
        
        # Log command
        self._log_command(chat_id, "unlink")
        
        account = TelegramAccount.query.filter_by(chat_id=str(chat_id), is_verified=True).first()
        
        if not account:
            await update.message.reply_text(
                "❌ No linked account found.\n"
                "Use /link to connect your account."
            )
            return
        
        # Create confirmation keyboard
        keyboard = [
            [
                InlineKeyboardButton("Yes, unlink", callback_data="unlink_confirm"),
                InlineKeyboardButton("Cancel", callback_data="unlink_cancel")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚠️ Are you sure you want to unlink your Telegram account?\n\n"
            "You will stop receiving notifications and approvals.",
            reply_markup=reply_markup
        )
    
    async def handle_pending(self, update: Update, context: CallbackContext):
        """Handle /pending command to show posts awaiting approval"""
        chat_id = update.effective_chat.id
        
        # Log command
        self._log_command(chat_id, "pending")
        
        # Get linked account
        account = TelegramAccount.query.filter_by(chat_id=str(chat_id), is_verified=True).first()
        
        if not account:
            await update.message.reply_text(
                "❌ Please link your account first using /link"
            )
            return
        
        # Get pending posts
        pending_posts = Post.query.join(PostApproval).filter(
            Post.client_id == account.client_id,
            PostApproval.status == 'pending'
        ).order_by(Post.scheduled_time).limit(5).all()
        
        if not pending_posts:
            await update.message.reply_text(
                "✨ No posts pending approval!\n"
                "All your scheduled posts are approved."
            )
            return
        
        await update.message.reply_text(
            f"📋 You have {len(pending_posts)} posts awaiting approval:"
        )
        
        # Send each pending post
        for post in pending_posts:
            await self.send_post_for_approval(chat_id, post)
    
    async def handle_stats(self, update: Update, context: CallbackContext):
        """Handle /stats command to show performance statistics"""
        chat_id = update.effective_chat.id
        
        # Log command
        self._log_command(chat_id, "stats")
        
        # Get linked account
        account = TelegramAccount.query.filter_by(chat_id=str(chat_id), is_verified=True).first()
        
        if not account:
            await update.message.reply_text(
                "❌ Please link your account first using /link"
            )
            return
        
        # Get client stats
        client = Client.query.get(account.client_id)
        if not client:
            await update.message.reply_text("❌ Error loading statistics")
            return
        
        # Calculate stats
        total_posts = Post.query.filter_by(client_id=client.id, status='published').count()
        posts_this_month = Post.query.filter(
            Post.client_id == client.id,
            Post.status == 'published',
            Post.published_time >= datetime.utcnow().replace(day=1)
        ).count()
        
        stats_text = (
            f"📊 *Performance Statistics*\n\n"
            f"*Company:* {client.company_name}\n"
            f"*Plan:* {client.subscription_plan.title()}\n\n"
            f"*Posts:*\n"
            f"• Total Published: {total_posts}\n"
            f"• This Month: {posts_this_month}\n"
            f"• Monthly Limit: {client.monthly_posts_limit}\n"
            f"• Remaining: {client.monthly_posts_limit - client.monthly_posts_used}\n\n"
            f"*AI Credits:*\n"
            f"• Used: {client.ai_credits_used}\n"
            f"• Limit: {client.ai_credits_limit}\n"
            f"• Remaining: {client.ai_credits_limit - client.ai_credits_used}"
        )
        
        await update.message.reply_text(stats_text, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_help(self, update: Update, context: CallbackContext):
        """Handle /help command"""
        chat_id = update.effective_chat.id
        
        # Log command
        self._log_command(chat_id, "help")
        
        help_text = (
            "🤖 *Kuwait Social AI Bot Commands*\n\n"
            "*Account Management:*\n"
            "/start - Start the bot\n"
            "/link <code> - Link your account\n"
            "/unlink - Disconnect your account\n\n"
            "*Post Management:*\n"
            "/pending - View posts awaiting approval\n"
            "/approve <id> - Quick approve a post\n"
            "/reject <id> - Quick reject a post\n\n"
            "*Analytics:*\n"
            "/stats - View your performance stats\n"
            "/today - Today's scheduled posts\n\n"
            "*Settings:*\n"
            "/settings - Manage notifications\n"
            "/language - Change language (EN/AR)\n\n"
            "*Support:*\n"
            "/help - Show this help message\n"
            "/support - Contact support\n\n"
            "💡 *Tip:* Use inline buttons for quick actions!"
        )
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_settings(self, update: Update, context: CallbackContext):
        """Handle /settings command"""
        chat_id = update.effective_chat.id
        
        # Log command
        self._log_command(chat_id, "settings")
        
        # Get linked account
        account = TelegramAccount.query.filter_by(chat_id=str(chat_id), is_verified=True).first()
        
        if not account:
            await update.message.reply_text(
                "❌ Please link your account first using /link"
            )
            return
        
        # Create settings keyboard
        keyboard = [
            [InlineKeyboardButton(
                f"{'✅' if account.notify_posts else '❌'} Post Notifications",
                callback_data="toggle_notify_posts"
            )],
            [InlineKeyboardButton(
                f"{'✅' if account.notify_analytics else '❌'} Analytics Updates",
                callback_data="toggle_notify_analytics"
            )],
            [InlineKeyboardButton(
                f"{'✅' if account.notify_alerts else '❌'} Important Alerts",
                callback_data="toggle_notify_alerts"
            )],
            [InlineKeyboardButton(
                f"Language: {'🇬🇧 English' if account.language_preference == 'en' else '🇰🇼 العربية'}",
                callback_data="toggle_language"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚙️ *Notification Settings*\n\n"
            "Choose what notifications you want to receive:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_callback(self, update: Update, context: CallbackContext):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        chat_id = query.message.chat_id
        
        # Get account
        account = TelegramAccount.query.filter_by(chat_id=str(chat_id)).first()
        
        if not account:
            await query.edit_message_text("❌ Session expired. Please use /start")
            return
        
        # Handle different callbacks
        if data == "unlink_confirm":
            account.is_verified = False
            account.chat_id = None
            db.session.commit()
            await query.edit_message_text(
                "✅ Your Telegram account has been unlinked.\n"
                "You can link it again anytime from your dashboard."
            )
        
        elif data == "unlink_cancel":
            await query.edit_message_text("❌ Unlink cancelled.")
        
        elif data.startswith("approve_"):
            post_id = int(data.replace("approve_", ""))
            await self._approve_post(query, post_id, account)
        
        elif data.startswith("reject_"):
            post_id = int(data.replace("reject_", ""))
            await self._reject_post(query, post_id, account)
        
        elif data.startswith("manual_"):
            post_id = int(data.replace("manual_", ""))
            await self._send_manual_package(query, post_id, account)
        
        elif data.startswith("toggle_"):
            await self._toggle_setting(query, data, account)
    
    async def handle_message(self, update: Update, context: CallbackContext):
        """Handle regular text messages"""
        chat_id = update.effective_chat.id
        text = update.message.text.strip()
        
        # Check if it might be a verification code
        if len(text) == 6 and text.isalnum():
            # Try to link with this code
            context.args = [text]
            await self.handle_link(update, context)
        else:
            await update.message.reply_text(
                "I didn't understand that. Try /help to see available commands."
            )
    
    async def send_post_for_approval(self, chat_id: str, post: Post) -> bool:
        """Send a post to Telegram for approval"""
        if not self.bot:
            logger.error("Telegram bot not initialized")
            return False
        
        try:
            # Format post preview
            preview_text = self._format_post_preview(post)
            
            # Create approval keyboard
            keyboard = [
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{post.id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{post.id}")
                ],
                [
                    InlineKeyboardButton("📤 Manual Post", callback_data=f"manual_{post.id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send message
            message = await self.bot.send_message(
                chat_id=chat_id,
                text=preview_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Create or update approval record
            approval = PostApproval.query.filter_by(post_id=post.id).first()
            if not approval:
                approval = PostApproval(post_id=post.id)
            
            approval.telegram_message_id = str(message.message_id)
            approval.status = 'pending'
            
            # Get telegram account
            telegram_account = TelegramAccount.query.filter_by(chat_id=chat_id).first()
            if telegram_account:
                approval.telegram_account_id = telegram_account.id
            
            db.session.add(approval)
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send post for approval: {e}")
            return False
    
    def _format_post_preview(self, post: Post) -> str:
        """Format post content for Telegram preview"""
        # Platform emoji mapping
        platform_emojis = {
            'instagram': '📷',
            'twitter': '🐦',
            'snapchat': '👻',
            'facebook': '📘',
            'linkedin': '💼'
        }
        
        platform_emoji = platform_emojis.get(post.platform.lower(), '📱')
        
        # Format scheduled time
        scheduled_time = post.scheduled_time.strftime("%Y-%m-%d %H:%M") if post.scheduled_time else "Not scheduled"
        
        # Truncate content if too long
        content = post.content
        if len(content) > 500:
            content = content[:497] + "..."
        
        # Format hashtags
        hashtags = " ".join(post.hashtags) if post.hashtags else "No hashtags"
        
        preview = (
            f"{platform_emoji} *New {post.platform.title()} Post*\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"*Content:*\n{content}\n\n"
            f"*Hashtags:*\n{hashtags}\n\n"
            f"*Scheduled:* {scheduled_time}\n"
            f"*Post ID:* #{post.id}"
        )
        
        # Add Arabic content if available
        if post.content_ar:
            arabic_content = post.content_ar
            if len(arabic_content) > 200:
                arabic_content = arabic_content[:197] + "..."
            preview += f"\n\n*Arabic Content:*\n{arabic_content}"
        
        return preview
    
    async def _approve_post(self, query, post_id: int, account: TelegramAccount):
        """Approve a post"""
        post = Post.query.get(post_id)
        if not post or post.client_id != account.client_id:
            await query.edit_message_text("❌ Post not found or access denied.")
            return
        
        # Update approval
        approval = PostApproval.query.filter_by(post_id=post_id).first()
        if approval:
            approval.approve(via='telegram')
            
        # Update post status
        post.status = 'approved'
        db.session.commit()
        
        # Update message
        await query.edit_message_text(
            f"✅ Post #{post_id} approved!\n\n"
            f"The post will be published at the scheduled time.\n"
            f"Platform: {post.platform}"
        )
        
        # Send notification to web app (if implemented)
        # self._notify_web_app('post_approved', {'post_id': post_id})
    
    async def _reject_post(self, query, post_id: int, account: TelegramAccount):
        """Reject a post"""
        post = Post.query.get(post_id)
        if not post or post.client_id != account.client_id:
            await query.edit_message_text("❌ Post not found or access denied.")
            return
        
        # Update approval
        approval = PostApproval.query.filter_by(post_id=post_id).first()
        if approval:
            approval.reject(reason="Rejected via Telegram")
        
        # Update post status
        post.status = 'rejected'
        db.session.commit()
        
        # Update message
        await query.edit_message_text(
            f"❌ Post #{post_id} rejected.\n\n"
            f"The post will not be published.\n"
            f"You can edit and resubmit it from the dashboard."
        )
    
    async def _send_manual_package(self, query, post_id: int, account: TelegramAccount):
        """Send manual posting package"""
        post = Post.query.get(post_id)
        if not post or post.client_id != account.client_id:
            await query.edit_message_text("❌ Post not found or access denied.")
            return
        
        # Update download count
        approval = PostApproval.query.filter_by(post_id=post_id).first()
        if approval:
            approval.manual_download_count += 1
            db.session.commit()
        
        # Format manual posting instructions
        instructions = self._format_manual_instructions(post)
        
        await query.edit_message_text(
            instructions,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    
    def _format_manual_instructions(self, post: Post) -> str:
        """Format manual posting instructions"""
        # Get optimal posting time
        optimal_time = "7:00 PM Kuwait Time"  # This could be dynamic based on analytics
        
        instructions = (
            f"📤 *Manual Posting Package*\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"*Platform:* {post.platform.title()}\n"
            f"*Best Time:* {optimal_time}\n\n"
            f"*📝 Caption:*\n"
            f"```\n{post.content}\n```\n\n"
        )
        
        if post.hashtags:
            instructions += f"*🏷️ Hashtags:*\n```\n{' '.join(post.hashtags)}\n```\n\n"
        
        if post.content_ar:
            instructions += f"*📝 Arabic Caption:*\n```\n{post.content_ar}\n```\n\n"
        
        instructions += (
            f"*💡 Instructions:*\n"
            f"1. Copy the caption above\n"
            f"2. Open {post.platform.title()}\n"
            f"3. Create new post\n"
            f"4. Paste caption and hashtags\n"
            f"5. Add your media files\n"
            f"6. Post at {optimal_time}\n\n"
            f"*📊 Pro Tip:* Posts at {optimal_time} get 40% more engagement!"
        )
        
        return instructions
    
    async def _toggle_setting(self, query, setting: str, account: TelegramAccount):
        """Toggle notification settings"""
        if setting == "toggle_notify_posts":
            account.notify_posts = not account.notify_posts
        elif setting == "toggle_notify_analytics":
            account.notify_analytics = not account.notify_analytics
        elif setting == "toggle_notify_alerts":
            account.notify_alerts = not account.notify_alerts
        elif setting == "toggle_language":
            account.language_preference = 'ar' if account.language_preference == 'en' else 'en'
        
        db.session.commit()
        
        # Refresh settings menu
        await self.handle_settings(query, None)
    
    def _log_command(self, chat_id: str, command: str, parameters: str = None):
        """Log telegram commands for analytics"""
        try:
            cmd_log = TelegramCommand(
                chat_id=str(chat_id),
                command=command,
                parameters=parameters,
                response_status='success'
            )
            db.session.add(cmd_log)
            db.session.commit()
        except Exception as e:
            logger.error(f"Failed to log command: {e}")
    
    async def send_notification(self, client_id: int, message: str, parse_mode: str = None):
        """Send a notification to a client via Telegram"""
        if not self.bot:
            return False
        
        # Get client's telegram account
        account = TelegramAccount.query.filter_by(
            client_id=client_id,
            is_verified=True,
            is_bot_active=True
        ).first()
        
        if not account or not account.chat_id:
            return False
        
        try:
            await self.bot.send_message(
                chat_id=account.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            
            # Update last interaction
            account.last_interaction = datetime.utcnow()
            db.session.commit()
            
            return True
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False


# Singleton instance
telegram_service = None


def get_telegram_service():
    """Get or create telegram service instance"""
    global telegram_service
    if telegram_service is None:
        telegram_service = TelegramService()
    return telegram_service