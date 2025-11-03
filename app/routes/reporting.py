from flask import Blueprint, render_template
from app.utils.db import assets_collection, work_orders_collection, inventory_collection

# 1. DEFINISIKAN BLUEPRINT
reporting_bp = Blueprint('reporting', __name__, template_folder='templates')

# 2. BUAT RUTE UNTUK DASHBOARD
@reporting_bp.route('/dashboard')
def dashboard():
    """Menampilkan halaman dashboard dengan data agregat."""
    
    # Inisialisasi data
    stats = {}

    try:
        # 1. Statistik Aset
        stats['total_assets'] = assets_collection.count_documents({})
        stats['assets_under_maintenance'] = assets_collection.count_documents({"status": "Under Maintenance"})

        # 2. Statistik Work Order
        stats['wo_open'] = work_orders_collection.count_documents({"status": "Open"})
        stats['wo_closed_total'] = work_orders_collection.count_documents({"status": "Closed"})

        # 3. Statistik Inventory
        stats['inventory_low_stock'] = list(inventory_collection.find({
            "$expr": {"$lte": ["$stock_on_hand", "$min_stock_level"]}
        }))
        stats['low_stock_count'] = len(stats['inventory_low_stock'])

        # 4. Agregasi Aset Paling Sering Rusak (Top 3)
        # Ini adalah query "Big Data" Anda
        stats['top_problem_assets'] = list(work_orders_collection.aggregate([
            { "$match": {"type": "Incident"} }, # Hanya hitung 'Insiden/Kerusakan'
            { "$group": {
                "_id": "$asset_name", # Kelompokkan berdasarkan nama aset
                "count": {"$sum": 1}  # Hitung jumlah insiden per aset
            }},
            { "$sort": {"count": -1} }, # Urutkan dari yang terbanyak
            { "$limit": 3 } # Ambil 3 teratas
        ]))

    except Exception as e:
        print(f"Error generating dashboard: {e}")
        stats = {} # Kosongkan jika ada error

    return render_template('dashboard.html', stats=stats)