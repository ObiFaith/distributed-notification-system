#!/usr/bin/env python
"""
Seed initial templates into the database
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Template, TemplateVersion

def seed_templates():
    """Seed initial templates"""
    app = create_app()
    
    with app.app_context():
        # Create tables first
        db.create_all()
        print("✅ Database tables created")
        
        print("🌱 Starting template seeding...")
        
        templates_to_create = [
            {
                'code': 'welcome_email',
                'name': 'Welcome Email',
                'notification_type': 'email',
                'subject': 'Welcome to {{app_name}}, {{name}}!',
                'body': '''Hi {{name}},

Welcome to {{app_name}}! We're excited to have you on board.

Get started by clicking here: {{link}}

If you have any questions, feel free to reach out to our support team.

Best regards,
The {{app_name}} Team''',
                'variables': ['name', 'app_name', 'link'],
                'description': 'Email sent to new users upon registration'
            },
            {
                'code': 'password_reset',
                'name': 'Password Reset Email',
                'notification_type': 'email',
                'subject': 'Reset Your Password',
                'body': '''Hi {{name}},

We received a request to reset your password.

Click here to reset: {{reset_link}}

This link will expire in {{expiry_hours}} hours.

If you didn't request this, please ignore this email.

Best regards,
The {{app_name}} Team''',
                'variables': ['name', 'reset_link', 'expiry_hours', 'app_name'],
                'description': 'Password reset email'
            },
            {
                'code': 'new_message_push',
                'name': 'New Message Push Notification',
                'notification_type': 'push',
                'body': '{{sender}} sent you a message: {{preview}}',
                'variables': ['sender', 'preview'],
                'description': 'Push notification for new messages'
            },
            {
                'code': 'account_verification',
                'name': 'Account Verification Email',
                'notification_type': 'email',
                'subject': 'Verify Your Email Address',
                'body': '''Hi {{name}},

Thank you for signing up! Please verify your email address to complete your registration.

Verification Link: {{verification_link}}

This link will expire in 24 hours.

Best regards,
The {{app_name}} Team''',
                'variables': ['name', 'verification_link', 'app_name'],
                'description': 'Email verification template'
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for template_data in templates_to_create:
            existing = Template.query.filter_by(code=template_data['code']).first()
            
            if not existing:
                template = Template(**template_data, version=1)
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
                
                print(f"  ✅ Created template: {template_data['code']}")
                created_count += 1
            else:
                print(f"  ⏭️  Template already exists: {template_data['code']}")
                skipped_count += 1
        
        db.session.commit()
        
        print(f"\n🎉 Template seeding complete!")
        print(f"  Created: {created_count}")
        print(f"  Skipped: {skipped_count}")

if __name__ == '__main__':
    try:
        seed_templates()
    except Exception as e:
        print(f"❌ Error seeding templates: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)