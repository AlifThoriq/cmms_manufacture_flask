from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.db import work_orders_collection, assets_collection
from bson.objectid import ObjectId
import datetime

# 1. DEFINISIKAN BLUEPRINT
work_orders_bp = Blueprint('work_orders', __name__, template_folder='templates')


# 2. BUAT RUTE UNTUK MELIHAT SEMUA WORK ORDER (YANG MASIH AKTIF)
@work_orders_bp.route('/')
def list_work_orders():
    """Menampilkan semua work order yang statusnya 'Open' atau 'In-Progress'."""
    try:
        # Cari semua WO yang belum selesai
        open_wos = list(work_orders_collection.find({
            "status": {"$in": ["Open", "In-Progress"]}
        }))
    except Exception as e:
        print(f"Error fetching open work orders: {e}")
        open_wos = []
        
    return render_template('work_order_list.html', work_orders=open_wos)


# 3. BUAT RUTE UNTUK MELIHAT HISTORI (YANG SUDAH SELESAI)
@work_orders_bp.route('/history')
def list_history():
    """Menampilkan semua work order yang statusnya 'Closed' (Maintenance History)."""
    try:
        # Cari semua WO yang sudah selesai
        closed_wos = list(work_orders_collection.find({"status": "Closed"}))
    except Exception as e:
        print(f"Error fetching closed work orders: {e}")
        closed_wos = []
        
    return render_template('history_list.html', work_orders=closed_wos)


# 4. BUAT RUTE UNTUK LAPOR KERUSAKAN (CREATE)
@work_orders_bp.route('/new/<asset_id>', methods=['GET', 'POST'])
def create_work_order(asset_id):
    """Form untuk membuat Work Order baru untuk aset spesifik."""
    try:
        asset = assets_collection.find_one({"_id": ObjectId(asset_id)})
        if not asset:
            return "Aset tidak ditemukan", 404
            
        if request.method == 'POST':
            wo_type = request.form['wo_type']
            title = request.form['title']
            description = request.form['description']
            priority = request.form['priority']
            
            new_wo = {
                "asset_id": ObjectId(asset_id),
                "asset_name": asset['asset_name'], # Simpan nama aset untuk kemudahan
                "type": wo_type, # Incident, Audit, Compliance
                "title": title,
                "description": description,
                "priority": priority,
                "status": "Open", # Status default
                "created_at": datetime.datetime.now(datetime.timezone.utc),
                "history_log": [
                    {
                        "timestamp": datetime.datetime.now(datetime.timezone.utc),
                        "user": "Operator", # (Nanti bisa diganti dgn user login)
                        "action": f"Work Order '{title}' dibuat."
                    }
                ]
            }
            
            work_orders_collection.insert_one(new_wo)
            
            # Update status aset menjadi 'Under Maintenance'
            assets_collection.update_one(
                {"_id": ObjectId(asset_id)},
                {"$set": {"status": "Under Maintenance"}}
            )
            
            return redirect(url_for('work_orders.list_work_orders'))

        return render_template('work_order_form.html', asset=asset)
        
    except Exception as e:
        print(f"Error creating work order: {e}")
        return "Error, ID aset tidak valid", 400


# 5. BUAT RUTE UNTUK MELIHAT DETAIL & MENUTUP WORK ORDER
@work_orders_bp.route('/<wo_id>', methods=['GET', 'POST'])
def detail_work_order(wo_id):
    """Menampilkan detail WO dan form untuk update (menambah log / menutup WO)."""
    try:
        wo = work_orders_collection.find_one({"_id": ObjectId(wo_id)})
        if not wo:
            return "Work Order tidak ditemukan", 404
        
        if request.method == 'POST':
            # Ini adalah form untuk 'Close Work Order'
            action_log = request.form['action_log']
            final_status = request.form['final_status'] # "Closed" atau "In-Progress"
            
            # Buat log histori baru
            new_log_entry = {
                "timestamp": datetime.datetime.now(datetime.timezone.utc),
                "user": "Teknisi", # (Nanti bisa diganti)
                "action": action_log
            }
            
            # Update Work Order di database
            work_orders_collection.update_one(
                {"_id": ObjectId(wo_id)},
                {
                    "$set": {"status": final_status},
                    "$push": {"history_log": new_log_entry}
                }
            )
            
            # Jika WO ditutup, ubah status Aset kembali ke 'Offline' atau 'Online'
            if final_status == 'Closed':
                assets_collection.update_one(
                    {"_id": wo['asset_id']},
                    # Asumsi kita set ke 'Offline', butuh pengecekan manual utk 'Online'
                    {"$set": {"status": "Offline"}} 
                )
                return redirect(url_for('work_orders.list_history'))

            return redirect(url_for('work_orders.detail_work_order', wo_id=wo_id))

        return render_template('work_order_detail.html', wo=wo)
        
    except Exception as e:
        print(f"Error fetching WO detail: {e}")
        return "Error, ID Work Order tidak valid", 400
    

@work_orders_bp.route('/tracking')
def list_tracking():
    """Menampilkan semua WO yang tipenya 'Audit' atau 'Compliance'."""
    try:
        tracked_items = list(work_orders_collection.find({
            "type": {"$in": ["Audit", "Compliance"]}
        }).sort("created_at", -1)) # Urutkan dari yang terbaru
    except Exception as e:
        print(f"Error fetching tracking items: {e}")
        tracked_items = []
        
    return render_template('tracking_list.html', items=tracked_items)