from flask import request, jsonify
from app.models import User, UserPreferences
from app import db
from app.schemas import validate_user_data, validate_login_data
from app.message_queue import mq
import logging
import uuid

logger = logging.getLogger(__name__)

def register_routes(app):
    
    @app.route('/')
    def index():
        return jsonify({
            'service': 'User Service',
            'version': '1.0.0',
            'status': 'running'
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200
    
    @app.route('/api/v1/users/', methods=['POST'])
    def create_user():
        """Create a new user"""
        try:
            data = request.get_json()
            
            errors = validate_user_data(data)
            if errors:
                return jsonify({'success': False, 'message': 'Validation error', 'errors': errors}), 400
            
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'success': False, 'message': 'User with this email already exists'}), 409
            
            user = User(
                name=data['name'],
                email=data['email']
            )
            user.set_password(data['password'])
            
            if 'preferences' in data:
                prefs_data = data['preferences']
                preferences = UserPreferences(
                    user=user,
                    email_notifications=prefs_data.get('email', True),
                    push_notifications=prefs_data.get('push', True)
                )
                db.session.add(preferences)
            
            db.session.add(user)
            db.session.commit()
            
            try:
                mq.publish(
                    routing_key='email.notify',
                    message={
                        'pattern': 'email.notify',
                        'data':{
                            'user_id': str(user.id),
                            'email': user.email,
                            'name': user.name,
                            'template_code': 'welcome_email',
                            'variables': {
                                'name': user.name,
                                'app_name': 'HNG Notification System',
                                'link': 'https://hng.tech/welcome'
                            },
                            'request_id': f'req-{uuid.uuid4()}'
                        }
                    }
                )
                logger.info(f"📤 Published welcome notification for user {user.email}")
            except Exception as e:
                logger.error(f"Failed to publish welcome notification: {e}")
            
            return jsonify({
                'success': True,
                'message': 'User created successfully',
                'data': user.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating user: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to create user'}), 500
    
    @app.route('/api/v1/users/<uuid:user_id>', methods=['GET'])
    def get_user(user_id):
        """Get user by ID"""
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            return jsonify({
                'success': True,
                'message': 'User retrieved successfully',
                'data': user.to_dict()
            }), 200
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to get user'}), 500
    
    @app.route('/api/v1/users/<uuid:user_id>', methods=['PUT'])
    def update_user(user_id):
        """Update user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            data = request.get_json()
            
            if 'name' in data:
                user.name = data['name']
            
            if 'email' in data:
                existing = User.query.filter_by(email=data['email']).first()
                if existing and existing.id != user.id:
                    return jsonify({'success': False, 'message': 'Email already taken'}), 400
                user.email = data['email']
            
            if 'password' in data:
                user.set_password(data['password'])
            
            if 'preferences' in data:
                prefs_data = data['preferences']
                if user.preferences:
                    user.preferences.email_notifications = prefs_data.get('email', user.preferences.email_notifications)
                    user.preferences.push_notifications = prefs_data.get('push', user.preferences.push_notifications)
                else:
                    preferences = UserPreferences(
                        user=user,
                        email_notifications=prefs_data.get('email', True),
                        push_notifications=prefs_data.get('push', True)
                    )
                    db.session.add(preferences)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'User updated successfully',
                'data': user.to_dict()
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating user: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to update user'}), 500
    
    @app.route('/api/v1/users/<uuid:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        """Delete user"""
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            db.session.delete(user)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'User deleted successfully'
            }), 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting user: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to delete user'}), 500
    
    @app.route('/api/v1/users/', methods=['GET'])
    def list_users():
        """List all users with pagination"""
        try:
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 10, type=int)
            
            page = max(1, page)
            limit = min(max(1, limit), 100)
            
            pagination = User.query.paginate(page=page, per_page=limit, error_out=False)
            users = [user.to_dict() for user in pagination.items]
            
            return jsonify({
                'success': True,
                'message': 'Users retrieved successfully',
                'data': users,
                'meta': {
                    'page': page,
                    'limit': limit,
                    'total': pagination.total,
                    'total_pages': pagination.pages
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to list users'}), 500
    
    @app.route('/api/v1/users/<uuid:user_id>/preferences', methods=['GET'])
    def get_user_preferences(user_id):
        """Get user notification preferences"""
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({'success': False, 'message': 'User not found'}), 404
            
            if not user.preferences:
                preferences = UserPreferences(
                    user=user,
                    email_notifications=True,
                    push_notifications=True
                )
                db.session.add(preferences)
                db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Preferences retrieved successfully',
                'data': user.preferences.to_dict()
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting preferences: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to get preferences'}), 500
    
    @app.route('/api/v1/auth/login', methods=['POST'])
    def login():
        """User login"""
        try:
            data = request.get_json()
            
            errors = validate_login_data(data)
            if errors:
                return jsonify({'success': False, 'message': 'Validation error', 'errors': errors}), 400
            
            user = User.query.filter_by(email=data['email']).first()
            
            if not user or not user.check_password(data['password']):
                return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
            
            token = f"token_{user.id}"
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'data': {
                    'token': token,
                    'user': user.to_dict()
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return jsonify({'success': False, 'message': 'Login failed'}), 500