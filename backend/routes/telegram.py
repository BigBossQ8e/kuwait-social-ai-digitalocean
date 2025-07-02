"""
Telegram API Routes for Kuwait Social AI
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import logging
import telegram

from models import db, User, Client, TelegramAccount, Post, PostApproval
from services.telegram_service import get_telegram_service
from services.telegram_bot_manager import get_bot_manager
from decorators import role_required

logger = logging.getLogger(__name__)

telegram_bp = Blueprint('telegram', __name__, url_prefix='/api/telegram')


@telegram_bp.route('/webhook', methods=['POST'])
def webhook():
    """Telegram webhook endpoint for bot updates"""
    try:
        telegram_service = get_telegram_service()
        if telegram_service and telegram_service.bot:
            update = telegram.Update.de_json(request.get_json(), telegram_service.bot)
            telegram_service.updater.dispatcher.process_update(update)
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 500


@telegram_bp.route('/bot/setup', methods=['POST'])
@jwt_required()
@role_required(['client', 'owner', 'admin'])
def setup_bot():
    """Setup client's Telegram bot with token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        data = request.get_json()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Validate required fields
        bot_token = data.get('bot_token')
        if not bot_token:
            return jsonify({'error': 'Bot token is required'}), 400
        
        # Get client
        client = None
        if user.role == 'client':
            client = user.client_profile
        elif user.role in ['owner', 'admin']:
            client_id = data.get('client_id')
            if client_id:
                client = Client.query.get(client_id)
        
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Validate bot token
        bot_manager = get_bot_manager()
        bot_info = bot_manager.validate_bot_token(bot_token)
        
        if not bot_info['valid']:
            return jsonify({
                'error': 'Invalid bot token',
                'details': bot_info.get('error', 'Token validation failed')
            }), 400
        
        # Check if telegram account exists
        telegram_account = TelegramAccount.query.filter_by(
            user_id=user.id,
            client_id=client.id
        ).first()
        
        if not telegram_account:
            telegram_account = TelegramAccount(
                user_id=user.id,
                client_id=client.id,
                telegram_id='',  # Will be set when user starts the bot
                chat_id=''  # Will be set when user starts the bot
            )
            db.session.add(telegram_account)
        
        # Update bot information
        telegram_account.bot_token = bot_token
        telegram_account.bot_username = bot_info['username']
        telegram_account.bot_name = bot_info['name']
        
        db.session.commit()
        
        # Initialize the bot
        success = bot_manager.add_bot(
            client.id,
            bot_token,
            bot_info['username']
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'bot_info': {
                    'username': bot_info['username'],
                    'name': bot_info['name'],
                    'link': f"https://t.me/{bot_info['username']}"
                },
                'message': f"Bot @{bot_info['username']} is now active! Users can start it to link their accounts."
            }), 200
        else:
            return jsonify({
                'error': 'Failed to initialize bot',
                'message': 'Bot token is valid but could not start the bot'
            }), 500
            
    except Exception as e:
        logger.error(f"Error setting up bot: {e}")
        return jsonify({'error': 'Failed to setup bot'}), 500


@telegram_bp.route('/bot/validate', methods=['POST'])
@jwt_required()
@role_required(['client', 'owner', 'admin'])
def validate_bot_token():
    """Validate a bot token without saving"""
    try:
        data = request.get_json()
        bot_token = data.get('bot_token')
        
        if not bot_token:
            return jsonify({'error': 'Bot token is required'}), 400
        
        bot_manager = get_bot_manager()
        bot_info = bot_manager.validate_bot_token(bot_token)
        
        if bot_info['valid']:
            return jsonify({
                'valid': True,
                'bot_info': {
                    'username': bot_info['username'],
                    'name': bot_info['name'],
                    'id': bot_info['id']
                }
            }), 200
        else:
            return jsonify({
                'valid': False,
                'error': bot_info.get('error', 'Invalid token')
            }), 400
            
    except Exception as e:
        logger.error(f"Error validating bot token: {e}")
        return jsonify({'error': 'Failed to validate token'}), 500


@telegram_bp.route('/link/request', methods=['POST'])
@jwt_required()
@role_required(['client', 'owner', 'admin'])
def request_link():
    """Request user to link their Telegram account to the client's bot"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get client
        client = None
        if user.role == 'client':
            client = user.client_profile
        elif user.role == 'owner':
            data = request.get_json()
            client_id = data.get('client_id')
            if client_id:
                client = Client.query.filter_by(id=client_id, owner_id=user.id).first()
        
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Check if already has a telegram account
        telegram_account = TelegramAccount.query.filter_by(
            user_id=user.id,
            client_id=client.id
        ).first()
        
        # Check if bot is configured
        if not telegram_account or not telegram_account.bot_token:
            return jsonify({
                'error': 'Bot not configured',
                'message': 'Please setup your Telegram bot first'
            }), 400
        
        if telegram_account.is_verified:
            return jsonify({
                'status': 'already_linked',
                'telegram_username': telegram_account.telegram_username,
                'linked_at': telegram_account.linked_at.isoformat() if telegram_account.linked_at else None
            }), 200
        
        # Return bot link for user to start
        return jsonify({
            'status': 'pending_link',
            'bot_username': telegram_account.bot_username,
            'bot_link': f"https://t.me/{telegram_account.bot_username}",
            'instructions': [
                f"1. Click the link to open @{telegram_account.bot_username}",
                "2. Press 'Start' button in Telegram",
                "3. The bot will guide you through the linking process"
            ]
        }), 200
        
    except Exception as e:
        logger.error(f"Error requesting telegram link: {e}")
        return jsonify({'error': 'Failed to generate verification code'}), 500


@telegram_bp.route('/link/status', methods=['GET'])
@jwt_required()
@role_required(['client', 'owner', 'admin'])
def link_status():
    """Check Telegram link status"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get telegram account
        telegram_account = TelegramAccount.query.filter_by(
            user_id=user.id,
            is_verified=True
        ).first()
        
        if not telegram_account:
            return jsonify({
                'status': 'not_linked',
                'message': 'No Telegram account linked'
            }), 200
        
        return jsonify({
            'status': 'linked',
            'telegram_username': telegram_account.telegram_username,
            'first_name': telegram_account.first_name,
            'last_name': telegram_account.last_name,
            'linked_at': telegram_account.linked_at.isoformat(),
            'is_bot_active': telegram_account.is_bot_active,
            'notifications': {
                'posts': telegram_account.notify_posts,
                'analytics': telegram_account.notify_analytics,
                'alerts': telegram_account.notify_alerts,
                'approvals': telegram_account.notify_approvals
            },
            'language': telegram_account.language_preference
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking telegram status: {e}")
        return jsonify({'error': 'Failed to check status'}), 500


@telegram_bp.route('/bot/remove', methods=['DELETE'])
@jwt_required()
@role_required(['client', 'owner', 'admin'])
def remove_bot():
    """Remove bot configuration and stop the bot"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get telegram account
        telegram_account = TelegramAccount.query.filter_by(
            user_id=user.id
        ).first()
        
        if not telegram_account or not telegram_account.bot_token:
            return jsonify({'error': 'No bot configured'}), 404
        
        # Stop the bot
        bot_manager = get_bot_manager()
        bot_manager.remove_bot(telegram_account.client_id)
        
        # Clear bot configuration
        telegram_account.bot_token = None
        telegram_account.bot_username = None
        telegram_account.bot_name = None
        telegram_account.webhook_url = None
        telegram_account.is_verified = False
        telegram_account.chat_id = None
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Bot removed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error removing bot: {e}")
        return jsonify({'error': 'Failed to remove bot'}), 500


@telegram_bp.route('/bot/instructions', methods=['GET'])
@jwt_required()
@role_required(['client', 'owner', 'admin'])
def get_bot_instructions():
    """Get instructions for creating a Telegram bot"""
    instructions = {
        'steps': [
            {
                'step': 1,
                'title': 'Open Telegram',
                'description': 'Open Telegram app on your phone or desktop'
            },
            {
                'step': 2,
                'title': 'Find BotFather',
                'description': 'Search for @BotFather and start a chat'
            },
            {
                'step': 3,
                'title': 'Create New Bot',
                'description': 'Send /newbot command to BotFather'
            },
            {
                'step': 4,
                'title': 'Choose Bot Name',
                'description': 'Enter a name for your bot (e.g., "My Restaurant Kuwait Bot")'
            },
            {
                'step': 5,
                'title': 'Choose Username',
                'description': 'Enter a unique username ending with "bot" (e.g., "MyRestaurantKuwaitBot")'
            },
            {
                'step': 6,
                'title': 'Copy Token',
                'description': 'BotFather will give you a token. Copy it and paste here.'
            }
        ],
        'tips': [
            'Keep your bot token secret - anyone with the token can control your bot',
            'You can customize your bot icon and description later',
            'Choose a memorable username - users will search for it'
        ],
        'video_tutorial': 'https://youtu.be/bot-creation-tutorial'  # Add actual video if available
    }
    
    return jsonify(instructions), 200


@telegram_bp.route('/unlink', methods=['POST'])
@jwt_required()
@role_required(['client', 'owner', 'admin'])
def unlink():
    """Unlink Telegram account"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get telegram account
        telegram_account = TelegramAccount.query.filter_by(
            user_id=user.id,
            is_verified=True
        ).first()
        
        if not telegram_account:
            return jsonify({'error': 'No linked Telegram account found'}), 404
        
        # Unlink the account
        telegram_account.is_verified = False
        telegram_account.chat_id = None
        telegram_account.telegram_id = None
        telegram_account.verification_code = None
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Telegram account unlinked successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error unlinking telegram: {e}")
        return jsonify({'error': 'Failed to unlink account'}), 500


@telegram_bp.route('/settings', methods=['PUT'])
@jwt_required()
@role_required(['client', 'owner', 'admin'])
def update_settings():
    """Update Telegram notification settings"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Get telegram account
        telegram_account = TelegramAccount.query.filter_by(
            user_id=current_user_id,
            is_verified=True
        ).first()
        
        if not telegram_account:
            return jsonify({'error': 'No linked Telegram account found'}), 404
        
        # Update settings
        if 'notify_posts' in data:
            telegram_account.notify_posts = data['notify_posts']
        if 'notify_analytics' in data:
            telegram_account.notify_analytics = data['notify_analytics']
        if 'notify_alerts' in data:
            telegram_account.notify_alerts = data['notify_alerts']
        if 'notify_approvals' in data:
            telegram_account.notify_approvals = data['notify_approvals']
        if 'language_preference' in data:
            telegram_account.language_preference = data['language_preference']
        if 'is_bot_active' in data:
            telegram_account.is_bot_active = data['is_bot_active']
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Settings updated successfully',
            'settings': {
                'notify_posts': telegram_account.notify_posts,
                'notify_analytics': telegram_account.notify_analytics,
                'notify_alerts': telegram_account.notify_alerts,
                'notify_approvals': telegram_account.notify_approvals,
                'language_preference': telegram_account.language_preference,
                'is_bot_active': telegram_account.is_bot_active
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating telegram settings: {e}")
        return jsonify({'error': 'Failed to update settings'}), 500


@telegram_bp.route('/send-test', methods=['POST'])
@jwt_required()
@role_required(['client', 'owner', 'admin'])
def send_test_message():
    """Send a test message to verify Telegram connection"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get telegram account
        telegram_account = TelegramAccount.query.filter_by(
            user_id=user.id,
            is_verified=True
        ).first()
        
        if not telegram_account:
            return jsonify({'error': 'No linked Telegram account found'}), 404
        
        # Get telegram service
        telegram_service = get_telegram_service()
        
        # Send test message
        test_message = (
            "🔔 *Test Notification*\n\n"
            "This is a test message from Kuwait Social AI.\n"
            "Your Telegram integration is working correctly! ✅"
        )
        
        success = telegram_service.send_notification(
            telegram_account.client_id,
            test_message,
            parse_mode='Markdown'
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Test message sent successfully'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to send test message'
            }), 500
            
    except Exception as e:
        logger.error(f"Error sending test message: {e}")
        return jsonify({'error': 'Failed to send test message'}), 500


@telegram_bp.route('/posts/<int:post_id>/prepare-manual', methods=['POST'])
@jwt_required()
@role_required(['client', 'owner', 'admin'])
def prepare_manual_post(post_id):
    """Prepare a post for manual publishing"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Get the post
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Check permissions
        if user.role == 'client' and post.client_id != user.client_profile.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Create or update approval record
        approval = PostApproval.query.filter_by(post_id=post_id).first()
        if not approval:
            approval = PostApproval(post_id=post_id)
        
        approval.status = 'approved'
        approval.approved_via = 'manual'
        approval.approved_at = datetime.utcnow()
        approval.manual_download_count = approval.manual_download_count + 1 if approval.manual_download_count else 1
        
        db.session.add(approval)
        db.session.commit()
        
        # Prepare manual posting package
        optimal_time = "7:00 PM Kuwait Time"  # This could be dynamic
        
        package = {
            'post_content': {
                'caption': post.content,
                'caption_arabic': post.content_ar,
                'hashtags': post.hashtags or [],
                'mentions': []  # Could extract from content
            },
            'platform_info': {
                'platform': post.platform,
                'optimal_time': optimal_time,
                'character_limit': {
                    'instagram': 2200,
                    'twitter': 280,
                    'snapchat': 250
                }.get(post.platform.lower(), 2000)
            },
            'instructions': {
                'best_time': optimal_time,
                'platforms': [post.platform],
                'notes': f'Posts at {optimal_time} typically get 40% more engagement'
            },
            'formatted_versions': {
                post.platform.lower(): _format_for_platform(post)
            }
        }
        
        return jsonify({
            'status': 'success',
            'package': package,
            'download_count': approval.manual_download_count
        }), 200
        
    except Exception as e:
        logger.error(f"Error preparing manual post: {e}")
        return jsonify({'error': 'Failed to prepare manual post'}), 500


@telegram_bp.route('/posts/<int:post_id>/send-approval', methods=['POST'])
@jwt_required()
@role_required(['client', 'owner', 'admin'])
def send_for_approval(post_id):
    """Send a post to Telegram for approval"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        # Get the post
        post = Post.query.get(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Check permissions
        if user.role == 'client' and post.client_id != user.client_profile.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Get client's telegram account
        telegram_account = TelegramAccount.query.filter_by(
            client_id=post.client_id,
            is_verified=True,
            is_bot_active=True,
            notify_approvals=True
        ).first()
        
        if not telegram_account:
            return jsonify({
                'error': 'No active Telegram account found for approval notifications'
            }), 400
        
        # Get client's bot
        bot_manager = get_bot_manager()
        client_bot = bot_manager.get_bot(post.client_id)
        
        if not client_bot:
            return jsonify({
                'error': 'Bot not initialized',
                'message': 'Please ensure the bot is properly configured'
            }), 400
        
        # Send post for approval
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(
            client_bot.send_post_for_approval(telegram_account.chat_id, post)
        )
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Post sent to Telegram for approval'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to send post to Telegram'
            }), 500
            
    except Exception as e:
        logger.error(f"Error sending post for approval: {e}")
        return jsonify({'error': 'Failed to send for approval'}), 500


def _format_for_platform(post):
    """Format post content for specific platform"""
    content = post.content
    hashtags = ' '.join(post.hashtags) if post.hashtags else ''
    
    if post.platform.lower() == 'twitter':
        # Twitter has 280 character limit
        max_length = 280 - len(hashtags) - 2  # Space and newline
        if len(content) > max_length:
            content = content[:max_length-3] + '...'
    
    elif post.platform.lower() == 'instagram':
        # Instagram allows up to 2200 characters
        # Add line breaks for better readability
        content = content.replace('. ', '.\n\n')
    
    elif post.platform.lower() == 'snapchat':
        # Snapchat prefers shorter content
        max_length = 250
        if len(content) > max_length:
            content = content[:max_length-3] + '...'
    
    # Combine content and hashtags
    if hashtags:
        formatted = f"{content}\n\n{hashtags}"
    else:
        formatted = content
    
    return formatted
