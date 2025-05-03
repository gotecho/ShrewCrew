from flask import Blueprint
from .routes.sms_routes import sms_bp
from .routes.webhook_routes import webhook_bp

routes_bp = Blueprint('routes_bp', __name__)

routes_bp.register_blueprint(sms_bp, url_prefix="/")
routes_bp.register_blueprint(webhook_bp, url_prefix="/")