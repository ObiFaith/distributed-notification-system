from flask import request, jsonify
from app.models import Template, TemplateVersion
from app import db
from app.schemas import validate_template_data
import logging

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
        """
        return jsonify({
            'service': 'Template Service',
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
        """
        return jsonify({'status': 'healthy'}), 200
    
    @app.route('/api/v1/templates/', methods=['POST'])
    def create_template():
        """
        Create a new notification template
        ---
        tags:
          - Templates
        parameters:
          - name: body
            in: body
            required: true
            schema:
              type: object
              required:
                - code
                - name
                - notification_type
                - body
              properties:
                code:
                  type: string
                  example: welcome_email
                  description: Unique template code
                name:
                  type: string
                  example: Welcome Email
                  description: Template display name
                notification_type:
                  type: string
                  enum: [email, push, sms]
                  example: email
                  description: Type of notification
                subject:
                  type: string
                  example: Welcome to HNG!
                  description: Email subject (for email templates)
                body:
                  type: string
                  example: Hello {{name}}, welcome to our platform!
                  description: Template body with variable placeholders
                variables:
                  type: array
                  items:
                    type: string
                  example: ["name", "app_name"]
                  description: List of available variables
                description:
                  type: string
                  example: Sent to new users upon registration
                  description: Template description
        responses:
          201:
            description: Template created successfully
          400:
            description: Validation error
          409:
            description: Template with this code already exists
          500:
            description: Server error
        """
        try:
            data = request.get_json()
            
            errors = validate_template_data(data)
            if errors:
                return jsonify({'success': False, 'message': 'Validation error', 'errors': errors}), 400
            
            existing = Template.query.filter_by(code=data['code']).first()
            if existing:
                return jsonify({'success': False, 'message': 'Template with this code already exists'}), 409
            
            template = Template(
                code=data['code'],
                name=data['name'],
                notification_type=data['notification_type'],
                subject=data.get('subject'),
                body=data['body'],
                variables=data.get('variables', []),
                description=data.get('description'),
                version=1
            )
            
            db.session.add(template)
            db.session.flush()
            
            version = TemplateVersion(
                template_id=template.id,
                version=1,
                subject=template.subject,
                body=template.body,
                variables=template.variables,
                change_notes='Initial template'
            )
            db.session.add(version)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Template created successfully',
                'data': template.to_dict()
            }), 201
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating template: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to create template'}), 500
    
    @app.route('/api/v1/templates/', methods=['GET'])
    def list_templates():
        """
        List all templates
        ---
        tags:
          - Templates
        responses:
          200:
            description: Templates retrieved successfully
            schema:
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: Templates retrieved successfully
                data:
                  type: array
                  items:
                    type: object
          500:
            description: Server error
        """
        try:
            templates = Template.query.all()
            return jsonify({
                'success': True,
                'message': 'Templates retrieved successfully',
                'data': [t.to_dict() for t in templates]
            }), 200
        except Exception as e:
            logger.error(f"Error listing templates: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to list templates'}), 500
    
    @app.route('/api/v1/templates/<template_code>', methods=['GET'])
    def get_template(template_code):
        """
        Get template by code
        ---
        tags:
          - Templates
        parameters:
          - name: template_code
            in: path
            type: string
            required: true
            description: Template code
            example: welcome_email
        responses:
          200:
            description: Template retrieved successfully
          404:
            description: Template not found
          500:
            description: Server error
        """
        try:
            template = Template.query.filter_by(code=template_code).first()
            if not template:
                return jsonify({'success': False, 'message': 'Template not found'}), 404
            
            return jsonify({
                'success': True,
                'message': 'Template retrieved successfully',
                'data': template.to_dict()
            }), 200
        except Exception as e:
            logger.error(f"Error getting template: {str(e)}")
            return jsonify({'success': False, 'message': 'Failed to get template'}), 500