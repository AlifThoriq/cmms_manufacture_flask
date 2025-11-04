from flask import Flask, render_template, redirect, url_for

def create_app():
    app = Flask(__name__)

    # --- TAMBAHAN BARU ---
    # Kunci ini diperlukan untuk session dan flash messages
    app.config['SECRET_KEY'] = 'kunci-rahasia-tim-anda-bisa-apa-saja'
    # ---------------------
    
    # Cek koneksi DB (opsional tapi bagus)
    from app.utils import db
    if db.client is None:
        print("Tidak bisa terhubung ke DB, aplikasi berhenti.")
        exit()

    # --- Daftarkan Blueprints (Rute) Anda di sini ---
    # --- Daftarkan Blueprints (Rute) Anda di sini ---
    from app.routes.assets import assets_bp
    app.register_blueprint(assets_bp, url_prefix='/assets')
    # BARU: Daftarkan blueprint work_orders
    from app.routes.work_orders import work_orders_bp
    app.register_blueprint(work_orders_bp, url_prefix='/work-orders')
    # BARU: Daftarkan blueprint inventory
    from app.routes.inventory import inventory_bp
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    # BARU: Daftarkan blueprint schedules
    from app.routes.schedules import schedules_bp
    app.register_blueprint(schedules_bp, url_prefix='/schedules')
    from app.routes.reporting import reporting_bp
    app.register_blueprint(reporting_bp, url_prefix='/reporting')

    # Buat 1 rute 'Home' sederhana untuk tes
    @app.route('/')
    def home():
        return redirect(url_for('reporting.dashboard'))

    return app
