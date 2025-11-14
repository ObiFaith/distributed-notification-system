from flask import request, jsonify
from flasgger import swag_from
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
        """
        Service Information
        ---
        tags:
          - Health
        responses:
          200:
            description: Service information
            schema:
              properties:
                service:
                  type: string
                  example: User Service
                version:
                  type: string
                  example: 1.0.0
                status:
                  type: string
                  example: running
        """
        return jsonify({
            'service': 'User Service',
            'version': '1.0.0',
            'status': 'running'
        })
    
    @app.route('/health')
    def health():
        """
        Health Check
        ---
        tags:
          - Health
        responses:
          200:
            description: Service is healthy
            schema:
              properties:
                status:
                  type: string
                  example: healthy
        """
        return jsonify({'status': 'healthy'}), 200
    
    @app.route('/api/v1/users/', methods=['POST'])
    def create_user():
        """
        Create a new user
        ---
        tags:
          - Users
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              required:
                - name
                - email
                - password
              properties:
                name:
                  type: string
                  example: John Doe
                  description: User's full name
                email:
                  type: string
                  example: john.doe@example.com
                  description: User's email address
                password:
                  type: string
                  example: SecurePass123
                  description: User's password (minimum 6 characters)
                preferences:
                  type: object
                  properties:
                    email:
                      type: boolean
                      example: true
                      description: Enable email notifications
                    push:
                      type: boolean
                      example: true
                      description: Enable push notifications
        responses:
          201:
            description: User created successfully
            schema:
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: User created successfully
                data:
                  type: object
                  properties:
                    id:
                      type: string
                      example: 550e8400-e29b-41d4-a716-446655440000
                    name:
                      type: string
                      example: John Doe
                    email:
                      type: string
                      example: john.doe@example.com
                    created_at:
                      type: string
                      example: 2025-11-12T04:00:00Z
          400:
            description: Validation error
          409:
            description: User already exists
          500:
            description: Server error
        """
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
                        "pattern": "email.notify",
                        "data": {
                            "notification_id": str(uuid.uuid4()),
                            "user_id": str(user.id),
                            "user_email": user.email,
                            "template_code": "welcome_email",
                            "variables": {
                                "name": user.name,
                                "app_name": "HNG Notification System",
                                "link": "https://hng.tech/welcome"
                            },
                            "request_id": f"req-{uuid.uuid4()}"
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
        """
        Get user by ID
        ---
        tags:
          - Users
        parameters:
          - name: user_id
            in: path
            type: string
            required: true
            description: User UUID
            example: 550e8400-e29b-41d4-a716-446655440000
        responses:
          200:
            description: User retrieved successfully
          404:
            description: User not found
          500:
            description: Server error
        """
        try:
            user = User.query.filter_by(id=user_id).first()
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
    
    @app.route('/api/v1/users/', methods=['GET'])
    def list_users():
        """
        List all users with pagination
        ---
        tags:
          - Users
        parameters:
          - name: page
            in: query
            type: integer
            default: 1
            description: Page number
          - name: limit
            in: query
            type: integer
            default: 10
            description: Number of items per page (max 100)
        responses:
          200:
            description: Users retrieved successfully
            schema:
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: Users retrieved successfully
                data:
                  type: array
                  items:
                    type: object
                meta:
                  type: object
                  properties:
                    page:
                      type: integer
                      example: 1
                    limit:
                      type: integer
                      example: 10
                    total:
                      type: integer
                      example: 50
                    total_pages:
                      type: integer
                      example: 5
          500:
            description: Server error
        """
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
    
    @app.route('/api/v1/auth/login', methods=['POST'])
    def login():
        """
        User login
        ---
        tags:
          - Authentication
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              required:
                - email
                - password
              properties:
                email:
                  type: string
                  example: john.doe@example.com
                password:
                  type: string
                  example: SecurePass123
        responses:
          200:
            description: Login successful
            schema:
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: Login successful
                data:
                  type: object
                  properties:
                    token:
                      type: string
                      example: token_550e8400-e29b-41d4-a716-446655440000
                    user:
                      type: object
          401:
            description: Invalid credentials
          500:
            description: Server error
        """
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
