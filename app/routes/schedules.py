from flask import Blueprint, render_template, request, redirect, url_for
from app.utils.db import schedules_collection, assets_collection
import datetime
from bson.objectid import ObjectId
from flask import abort


# 1. DEFINISIKAN BLUEPRINT
schedules_bp = Blueprint('schedules', __name__, template_folder='templates')

# 2. BUAT RUTE UNTUK MELIHAT DAFTAR JADWAL (Read)
@schedules_bp.route('/')
def list_schedules():
    """Menampilkan halaman daftar semua jadwal perawatan preventif."""
    
    # Tentukan hari ini (menggunakan UTC agar konsisten dengan database)
    today = datetime.datetime.now(datetime.timezone.utc)
    
    processed_schedules = []
    urgent_items = [] # Daftar untuk menyimpan nama item yang mendesak

    try:
        all_schedules = list(schedules_collection.find().sort("next_due_date", 1))
        
        for schedule in all_schedules:
            # Pastikan next_due_date adalah datetime object yang aware (zona UTC)
            if schedule['next_due_date'].tzinfo is None:
                schedule['next_due_date'] = schedule['next_due_date'].replace(tzinfo=datetime.timezone.utc)

            # Hitung sisa hari
            delta = schedule['next_due_date'] - today
            days_remaining = delta.days

            # Terapkan logika status berdasarkan sisa hari
            if days_remaining < 0:
                schedule['status_text'] = "WAJIB DIGANTI"
                schedule['status_color'] = "red"
                urgent_items.append(schedule['task_name']) # Tambahkan ke daftar alert
            elif 0 <= days_remaining <= 3:
                schedule['status_text'] = "SEGERA DIGANTI"
                schedule['status_color'] = "orange"
                urgent_items.append(schedule['task_name']) # Tambahkan ke daftar alert
            else:
                schedule['status_text'] = "AMAN"
                schedule['status_color'] = "green"
            
            processed_schedules.append(schedule)

    except Exception as e:
        print(f"Error fetching or processing schedules: {e}")
        processed_schedules = []
        
    return render_template(
        'schedule_list.html', 
        schedules=processed_schedules,
        urgent_items=urgent_items  # Kirim daftar item mendesak ke template
    )

# 3. BUAT RUTE UNTUK MENAMBAH JADWAL (Create)
@schedules_bp.route('/add', methods=['GET', 'POST'])
def add_schedule():
    """Menampilkan form untuk menambah jadwal baru (GET) atau memproses form (POST)."""
    if request.method == 'POST':
        task_name = request.form['task_name']
        asset_type = request.form['asset_type'] 
        frequency_days = int(request.form['frequency_days'])
        
        # Tentukan waktu saat ini dalam UTC
        current_time_utc = datetime.datetime.now(datetime.timezone.utc)
        
        # Hitung tanggal jatuh tempo pertama
        next_due_date = current_time_utc + datetime.timedelta(days=frequency_days)
        
        new_schedule = {
            "task_name": task_name,
            "asset_type": asset_type,
            "frequency_days": frequency_days,
            "next_due_date": next_due_date,
            "last_completed": None,
            # --- BARIS BARU DITAMBAHKAN ---
            "last_updated": current_time_utc 
            # --------------------------------
        }
        
        try:
            schedules_collection.insert_one(new_schedule)
        except Exception as e:
            print(f"Error inserting schedule: {e}")
            
        return redirect(url_for('schedules.list_schedules'))

    # Jika method GET, ambil daftar tipe aset untuk dropdown
    asset_types = ["All"] + assets_collection.distinct("type")
    return render_template('schedule_form.html', asset_types=asset_types)

@schedules_bp.route('/detail/<schedule_id>')
def detail_schedule(schedule_id):
    """Menampilkan detail dari satu jadwal perawatan preventif."""
    try:
        schedule = schedules_collection.find_one({"_id": ObjectId(schedule_id)})
        if not schedule:
            abort(404, description="Jadwal tidak ditemukan.")
    except Exception as e:
        print(f"Error fetching schedule detail: {e}")
        abort(500, description="Terjadi kesalahan pada server.")
    
    # Format tanggal agar tidak error di template
    for field in ["last_updated", "next_due_date", "last_completed"]:
        if field in schedule and schedule[field]:
            schedule[field] = schedule[field].astimezone(datetime.timezone(datetime.timedelta(hours=7)))  # Ubah ke WIB jika perlu
    
    return render_template("schedule_detail.html", schedule=schedule)

@schedules_bp.route('/delete/<schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):
    """Menghapus jadwal perawatan berdasarkan ID."""
    try:
        result = schedules_collection.delete_one({"_id": ObjectId(schedule_id)})
        if result.deleted_count == 0:
            abort(404, description="Jadwal tidak ditemukan atau sudah dihapus.")
    except Exception as e:
        print(f"Error deleting schedule: {e}")
        abort(500, description="Terjadi kesalahan saat menghapus jadwal.")
    
    return redirect(url_for('schedules.list_schedules'))


@schedules_bp.route('/maintenance/<schedule_id>', methods=['GET', 'POST'])
def schedule_maintenance(schedule_id):
    try:
        schedule = schedules_collection.find_one({"_id": ObjectId(schedule_id)})
        if not schedule:
            abort(404, description="Jadwal tidak ditemukan.")
    except Exception as e:
        print(f"Error fetching schedule for maintenance: {e}")
        abort(500, description="Terjadi kesalahan saat mengambil data jadwal.")

    if request.method == 'POST':
        priority = request.form.get('priority')
        description = request.form.get('description')

        current_time = datetime.datetime.now(datetime.timezone.utc)
        schedules_collection.update_one(
            {"_id": ObjectId(schedule_id)},
            {"$set": {
                "last_completed": current_time,
                "last_updated": current_time,
                "last_description": description,
                "last_priority": priority
            }}
        )

        return redirect(url_for('schedules.list_schedules'))

    return render_template('schedule_form_maintenance.html', schedule=schedule)

