from flask import Blueprint, render_template, request, redirect, url_for
from app.utils.db import schedules_collection, assets_collection
import datetime

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