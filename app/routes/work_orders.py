from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.db import work_orders_collection, assets_collection
from app.utils.db import work_orders_collection, assets_collection, inventory_collection
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


# 4. RUTE BUAT WO BARU (LOGIKA BARU SESUAI IDE ANDA)
@work_orders_bp.route('/new/<asset_id>', methods=['GET', 'POST'])
def create_work_order(asset_id):
    """
    GET: Menampilkan form WO baru + checklist komponen.
    POST: Membuat 1 WO, dan meng-update status SEMUA komponen yang di-checklist.
    """
    try:
        asset = assets_collection.find_one({"_id": ObjectId(asset_id)})
        if not asset:
            return "Aset tidak ditemukan", 404
            
        # --- LOGIKA POST (BARU) ---
        if request.method == 'POST':
            # 1. Ambil data form dasar
            title = request.form['title']
            description = request.form['description']
            priority = request.form['priority']
            
            # 2. Ambil daftar komponen yang di-checklist
            # request.form.getlist() sangat penting untuk mengambil semua value dari checkbox
            komponen_rusak_ids = request.form.getlist('komponen_rusak') 
            
            # 3. Update status komponen di database aset
            if komponen_rusak_ids:
                # Set semua komponen yang di-checklist menjadi "Critical / Down"
                assets_collection.update_one(
                    {"_id": ObjectId(asset_id)},
                    {"$set": {"components.$[elem].status": "Critical / Down"}},
                    array_filters=[{"elem.component_id": {"$in": komponen_rusak_ids}}]
                )
            
            # 4. Buat 1 Work Order
            current_time = datetime.datetime.now(datetime.timezone.utc)
            new_wo = {
                "asset_id": ObjectId(asset_id),
                "asset_name": asset['asset_name'], 
                "type": "Incident", # Tipe default untuk laporan manual
                "title": title,
                "description": description,
                "priority": priority,
                "status": "Open", 
                "created_at": current_time,
                "related_components": komponen_rusak_ids, # <-- KITA SIMPAN KOMPONEN RUSAK
                "history_log": [
                    {
                        "timestamp": current_time,
                        "user": "Operator", # (Nanti bisa diganti dgn user login)
                        "action": f"Work Order '{title}' dibuat. Melaporkan {len(komponen_rusak_ids)} komponen."
                    }
                ]
            }
            work_orders_collection.insert_one(new_wo)
            
            # 5. Update status aset utama
            assets_collection.update_one(
                {"_id": ObjectId(asset_id)},
                {"$set": {"status": "Under Maintenance"}}
            )
            
            flash("✅ Work Order berhasil dibuat!", "success")
            return redirect(url_for('work_orders.list_work_orders'))

        # --- LOGIKA GET (BARU) ---
        # Kirim daftar komponen aset ke form
        return render_template('work_order_form.html', asset=asset)
        
    except Exception as e:
        print(f"Error creating work order: {e}")
        return "Error, ID aset tidak valid", 400


# --- INI BAGIAN UTAMA YANG DIUBAH (DETAIL & LOGIKA INVENTORY) ---
@work_orders_bp.route('/<wo_id>', methods=['GET', 'POST'])
def detail_work_order(wo_id):
    try:
        wo = work_orders_collection.find_one({"_id": ObjectId(wo_id)})
        if not wo:
            return "Work Order tidak ditemukan", 404
        
        if request.method == 'POST':
            action_log = request.form['action_log']
            final_status = request.form['final_status']
            
            # Ambil data part dari form (jika ada)
            part_id = request.form.get('part_id')
            quantity_used = int(request.form.get('quantity_used', 0))

            current_time = datetime.datetime.now(datetime.timezone.utc)
            logs_to_add = []
            parts_data_to_push = None

            # 1. LOGIKA INVENTORY (Hanya jika user memilih part & jumlah > 0)
            if part_id and quantity_used > 0:
                # Cek stok dulu
                part = inventory_collection.find_one({"_id": ObjectId(part_id)})
                
                if part and part.get('stock_on_hand', 0) >= quantity_used:
                    # Kurangi Stok
                    inventory_collection.update_one(
                        {"_id": ObjectId(part_id)},
                        {"$inc": {"stock_on_hand": -quantity_used}}
                    )
                    
                    part_name = part.get('part_name')
                    
                    # Catat untuk History Log (Teks)
                    log_message_part = f"Mengambil {quantity_used} unit '{part_name}' dari Gudang."
                    logs_to_add.append({
                        "timestamp": current_time,
                        "user": "Teknisi",
                        "action": log_message_part
                    })

                    # Catat untuk Tabel 'Barang yang Diambil' (Data Terstruktur)
                    parts_data_to_push = {
                        "part_id": str(part_id),
                        "part_name": part_name,
                        "quantity": quantity_used,
                        "taken_at": current_time
                    }
                    
                    flash(f"Berhasil mengambil {quantity_used} {part_name}. Stok berkurang.", "success")
                else:
                    flash("Gagal! Stok di gudang tidak mencukupi.", "error")
                    return redirect(url_for('work_orders.detail_work_order', wo_id=wo_id))

            # 2. Catat Log Tindakan Manual (Ketikam user)
            logs_to_add.append({
                "timestamp": current_time,
                "user": "Teknisi",
                "action": f"Update Status: {final_status}. Catatan: {action_log}"
            })

            # 3. SUSUN QUERY UPDATE DATABASE
            update_query = {
                "$set": {"status": final_status},
                "$push": {"history_log": {"$each": logs_to_add}}
            }

            # Jika ada part yang diambil, masukkan ke array 'used_parts'
            if parts_data_to_push:
                # Kita gunakan $push lagi untuk used_parts
                if "used_parts" not in update_query["$push"]:
                     update_query["$push"]["used_parts"] = parts_data_to_push
                else:
                     # Jika query complex, lakukan 2 update terpisah atau gunakan list extension (disini saya pisah logic biar aman)
                     work_orders_collection.update_one(
                         {"_id": ObjectId(wo_id)}, 
                         {"$push": {"used_parts": parts_data_to_push}}
                     )

            # Eksekusi Update Utama
            work_orders_collection.update_one({"_id": ObjectId(wo_id)}, update_query)
            
            # 4. LOGIKA JIKA CLOSED (Reset Aset)
            if final_status == 'Closed':
                assets_collection.update_one(
                    {"_id": wo['asset_id']},
                    {"$set": {"status": "Operational"}}
                )
                # Reset komponen yang rusak jadi Good
                component_ids_to_fix = wo.get('related_components')
                if component_ids_to_fix:
                    assets_collection.update_one(
                        {"_id": wo['asset_id']},
                        {"$set": {"components.$[elem].status": "Good / Operational"}},
                        array_filters=[{"elem.component_id": {"$in": component_ids_to_fix}}]
                    )
                flash("Work Order Ditutup. Aset kembali Operasional.", "success")
                return redirect(url_for('work_orders.list_history'))

            return redirect(url_for('work_orders.detail_work_order', wo_id=wo_id))

        # --- LOGIKA GET ---
        # Ambil daftar inventory yang stoknya > 0 untuk dropdown
        inventory_parts = list(inventory_collection.find({"stock_on_hand": {"$gt": 0}}))
        
        return render_template(
            'work_order_detail.html', 
            wo=wo, 
            inventory_parts=inventory_parts
        )
        
    except Exception as e:
        print(f"Error detail WO: {e}")
        return "Terjadi kesalahan sistem", 500