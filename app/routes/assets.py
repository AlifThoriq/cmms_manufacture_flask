from flask import Blueprint, render_template, request, redirect, url_for
from app.utils.db import assets_collection
from bson.objectid import ObjectId
from app.utils.db import assets_collection, schedules_collection

# 1. DEFINISIKAN BLUEPRINT
assets_bp = Blueprint('assets', __name__, template_folder='templates')

# 2. DEFINISIKAN DATA KOMPONEN (SESUAI DAFTAR ANDA)
COMPONENT_TEMPLATES = {
    "Crusher": [
        {"name": "Jaw plate", "type": "routine", "status": "Good"},
        {"name": "Concave / Mantle (cone)", "type": "routine", "status": "Good"},
        {"name": "Flywheel", "type": "incidental", "status": "Good"},
        {"name": "Toggle plate", "type": "routine", "status": "Good"},
        {"name": "Eccentric shaft", "type": "incidental", "status": "Good"},
        {"name": "Main shaft", "type": "incidental", "status": "Good"},
        {"name": "Frame / chassis", "type": "incidental", "status": "Good"},
        {"name": "Motor listrik utama", "type": "incidental", "status": "Good"},
        {"name": "Coupling", "type": "routine", "status": "Good"},
        {"name": "Gearbox / reducer", "type": "incidental", "status": "Good"},
        {"name": "Bearing (utama)", "type": "routine", "status": "Good"},
        {"name": "Lubrication pump", "type": "routine", "status": "Good"},
        {"name": "Oil filter", "type": "routine", "status": "Good"},
        {"name": "Hopper / feed chute", "type": "routine", "status": "Good"},
        {"name": "Feeder (vibrating feeder)", "type": "routine", "status": "Good"},
        {"name": "Discharge chute / grate", "type": "routine", "status": "Good"},
        {"name": "Belt conveyor (input)", "type": "routine", "status": "Good"},
        {"name": "Belt conveyor (output)", "type": "routine", "status": "Good"},
        {"name": "Proximity sensor (feed)", "type": "routine", "status": "Good"},
        {"name": "Vibration sensor (bearing)", "type": "routine", "status": "Good"},
        {"name": "Dust collector / baghouse connection", "type": "incidental", "status": "Good"},
        {"name": "Control panel / PLC", "type": "incidental", "status": "Good"}
    ],
    "Ball Mill": [
        # TODO: Masukkan 24 komponen Ball Mill Anda di sini
        {"name": "Drum / shell", "type": "incidental", "status": "Good"},
        {"name": "Liner (crusher liners)", "type": "routine", "status": "Good"},
        # ... (dan seterusnya)
    ],
    "Flotation Cell": [
        # TODO: Masukkan 20 komponen Flotation Cell Anda di sini
        {"name": "Tank / cell body", "type": "incidental", "status": "Good"},
        {"name": "Impeller / agitator", "type": "routine", "status": "Good"},
        # ... (dan seterusnya)
    ],
    "Smelter / Furnace": [
        # TODO: Masukkan 22 komponen Smelter Anda di sini
        {"name": "Burner / heating element", "type": "incidental", "status": "Good"},
        {"name": "Furnace shell / hearth", "type": "incidental", "status": "Good"},
        # ... (dan seterusnya)
    ]
}


# 3. BUAT RUTE UNTUK MELIHAT DAFTAR ASET (Read)
@assets_bp.route('/')
def list_assets():
    """Menampilkan halaman daftar semua aset."""
    try:
        all_assets = list(assets_collection.find())
    except Exception as e:
        print(f"Error fetching assets: {e}")
        all_assets = []
        
    return render_template('assets_list.html', assets=all_assets)

# 🔹 RUTE UNTUK MENAMPILKAN ASET DALAM PERBAIKAN
@assets_bp.route('/under_maintenance')
def assets_under_maintenance():
    """Menampilkan daftar aset yang sedang dalam status 'Under Maintenance'."""
    try:
        # Ambil semua aset dengan status "Under Maintenance"
        under_maintenance_assets = list(assets_collection.find({"status": "Under Maintenance"}))
    except Exception as e:
        print(f"Error fetching assets under maintenance: {e}")
        under_maintenance_assets = []
        
    return render_template('assets_under_maintenance.html', assets=under_maintenance_assets)

# 4. BUAT RUTE UNTUK MENAMBAH ASET (Create)
@assets_bp.route('/add', methods=['GET', 'POST'])
def add_asset():
    """Menampilkan form untuk menambah aset (GET) atau memproses form (POST)."""
    if request.method == 'POST':
        asset_name = request.form['asset_name']
        asset_type = request.form['asset_type'] # Misal: "Crusher"
        location = request.form['location']

        # Ambil template komponen berdasarkan tipenya
        components_list = COMPONENT_TEMPLATES.get(asset_type, [])
        
        new_asset = {
            "asset_name": asset_name,
            "type": asset_type,
            "location": location,
            "status": "Offline", # Status default saat baru ditambahkan
            "monitoring_data": {}, # Data monitoring awal (kosong)
            "total_runtime_hours": 0,
            "components": components_list # Langsung masukkan daftar komponennya
        }
        
        try:
            assets_collection.insert_one(new_asset)
        except Exception as e:
            print(f"Error inserting asset: {e}")
            
        return redirect(url_for('assets.list_assets'))

    # Jika method GET, tampilkan form
    return render_template('assets_form.html')


# 5. BUAT RUTE UNTUK MELIHAT DETAIL ASET
@assets_bp.route('/<asset_id>')
def detail_asset(asset_id):
    """Menampilkan halaman detail untuk satu aset spesifik."""
    try:
        asset = assets_collection.find_one({"_id": ObjectId(asset_id)})
        if not asset:
            return "Aset tidak ditemukan", 404

        # --- TAMBAHAN BARU ---
        # Cari jadwal yang relevan untuk tipe aset ini
        relevant_schedules = list(schedules_collection.find({
            "$or": [
                {"asset_type": asset['type']}, # Misal: Jadwal untuk "Crusher"
                {"asset_type": "All"}          # Misal: Jadwal untuk "Semua"
            ]
        }).sort("next_due_date", 1))
        # ---------------------

        return render_template('assets_detail.html', 
                               asset=asset, 
                               schedules=relevant_schedules) # Kirim data jadwal ke template
    except Exception as e:
        print(f"Error fetching asset detail: {e}")
        return "Error, ID aset tidak valid", 400
    
# 6. RUTE UNTUK UPDATE STATUS ATAU DATA ASET
@assets_bp.route('/update_asset/<asset_id>', methods=['POST'])
def update_asset(asset_id):
    """Memperbarui data aset (misalnya status, lokasi, dll)."""
    try:
        new_status = request.form.get('status')
        new_location = request.form.get('location')

        update_data = {}
        if new_status:
            update_data["status"] = new_status
        if new_location:
            update_data["location"] = new_location

        if update_data:
            assets_collection.update_one(
                {"_id": ObjectId(asset_id)},
                {"$set": update_data}
            )

        # ✅ tampilkan alert sukses dengan flash message
        from flask import flash
        flash("Data aset berhasil diperbarui!", "success")
    except Exception as e:
        print(f"Error updating asset: {e}")
        flash("Gagal memperbarui data aset.", "error")

    return redirect(url_for('assets.detail_asset', asset_id=asset_id))
