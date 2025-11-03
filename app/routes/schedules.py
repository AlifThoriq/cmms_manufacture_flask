from flask import Blueprint, render_template, request, redirect, url_for
from app.utils.db import schedules_collection, assets_collection
import datetime

# 1. DEFINISIKAN BLUEPRINT
schedules_bp = Blueprint('schedules', __name__, template_folder='templates')

# 2. BUAT RUTE UNTUK MELIHAT DAFTAR JADWAL (Read)
@schedules_bp.route('/')
def list_schedules():
    """Menampilkan halaman daftar semua jadwal perawatan preventif."""
    try:
        all_schedules = list(schedules_collection.find().sort("next_due_date", 1))
    except Exception as e:
        print(f"Error fetching schedules: {e}")
        all_schedules = []
        
    return render_template('schedule_list.html', schedules=all_schedules)

# 3. BUAT RUTE UNTUK MENAMBAH JADWAL (Create)
@schedules_bp.route('/add', methods=['GET', 'POST'])
def add_schedule():
    """Menampilkan form untuk menambah jadwal baru (GET) atau memproses form (POST)."""
    if request.method == 'POST':
        task_name = request.form['task_name']
        asset_type = request.form['asset_type'] # Misal: "Crusher", "Ball Mill", atau "All"
        frequency_days = int(request.form['frequency_days'])
        
        # Hitung tanggal jatuh tempo pertama (dari hari ini)
        next_due_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=frequency_days)
        
        new_schedule = {
            "task_name": task_name,
            "asset_type": asset_type,
            "frequency_days": frequency_days,
            "next_due_date": next_due_date,
            "last_completed": None
        }
        
        try:
            schedules_collection.insert_one(new_schedule)
        except Exception as e:
            print(f"Error inserting schedule: {e}")
            
        return redirect(url_for('schedules.list_schedules'))

    # Jika method GET, ambil daftar tipe aset untuk dropdown
    asset_types = ["All"] + assets_collection.distinct("type")
    return render_template('schedule_form.html', asset_types=asset_types)