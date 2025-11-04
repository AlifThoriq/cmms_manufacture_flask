from flask import Flask

# Import semua blueprint
from app.routes.assets import assets_bp
from app.routes.inventory import inventory_bp
from app.routes.reporting import reporting_bp
from app.routes.schedules import schedules_bp
from app.routes.work_orders import work_orders_bp

def create_app():
    app = Flask(__name__)

    # Registrasi semua blueprint
    app.register_blueprint(assets_bp, url_prefix='/assets')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(reporting_bp, url_prefix='/reporting')
    app.register_blueprint(schedules_bp, url_prefix='/schedules')
    app.register_blueprint(work_orders_bp, url_prefix='/work_orders')

    return app
