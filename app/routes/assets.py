from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.utils.db import assets_collection, schedules_collection
from bson.objectid import ObjectId

# -----------------------------
# 1. DEFINISI BLUEPRINT
# -----------------------------
assets_bp = Blueprint('assets', __name__, template_folder='templates')


# -----------------------------
# 2. DEFINISI STATUS & KONFIGURASI
# -----------------------------

# Status Komponen Standar Industri CMMS
COMPONENT_STATUSES = [
    "Good",
    "Warning",
    "Degraded",
    "Critical",
    "Down",
    "Repaired"
]

# Kategori Maintenance Standar
MAINTENANCE_CATEGORIES = [
    "Preventive",
    "Corrective",
    "Condition-Based",
    "Corrective",
    "Breakdown",
    "Shutdown"
]

# Placeholder Gambar Mesin (Gunakan URL gambar nyata Anda)
MACHINE_IMAGE_URLS = {
    "Crusher": "/static/img/crusher.png",
    "Ball Mill": "/static/img/ball mill.png",
    "Flotation Cell": "/static/img/flotation.png",
    "Smelter / Furnace": "/static/img/smelter.png"
}

# -----------------------------
# 3. TEMPLATE KOMPONEN BARU
# -----------------------------
# Status default diubah menjadi "Operational" dan kategori disesuaikan
COMPONENT_TEMPLATES = {
    "Crusher": [
        {"component_id": "C001", "name": "Jaw plate", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C002", "name": "Concave / Mantle (cone)", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C003", "name": "Flywheel", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C004", "name": "Toggle plate", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C005", "name": "Eccentric shaft", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C006", "name": "Main shaft", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C007", "name": "Frame / chassis", "category": MAINTENANCE_CATEGORIES[3], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C008", "name": "Motor listrik utama", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C009", "name": "Coupling", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C010", "name": "Gearbox / reducer", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C011", "name": "Bearing (utama)", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C012", "name": "Lubrication pump", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C013", "name": "Oil filter", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C014", "name": "Hopper / feed chute", "category": MAINTENANCE_CATEGORIES[3], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C015", "name": "Feeder (vibrating feeder)", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C016", "name": "Discharge chute / grate", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C017", "name": "Belt conveyor (input)", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C018", "name": "Belt conveyor (output)", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C019", "name": "Proximity sensor (feed)", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C020", "name": "Vibration sensor (bearing)", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C021", "name": "Dust collector / baghouse connection", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "C022", "name": "Control panel / PLC", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]}
    ],
    "Ball Mill": [
        {"component_id": "B001", "name": "Drum / shell", "category": MAINTENANCE_CATEGORIES[3], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B002", "name": "Liner (crusher liners)", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B003", "name": "Trunnion bearing", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B004", "name": "Main bearing", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B005", "name": "Gear ring & pinion", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B006", "name": "Mill motor (ball mill drive)", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B007", "name": "Coupling & clutch", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B008", "name": "Lubrication system", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B009", "name": "Bearing temperature sensor", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B010", "name": "Vibration sensor", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B011", "name": "Feed chute / trommel feeder", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B012", "name": "Discharge grate / classifier", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B013", "name": "Grinding media (balls)", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B014", "name": "Mill speed sensor", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B015", "name": "Seals & gland", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B016", "name": "Mill foundation / baseplate", "category": MAINTENANCE_CATEGORIES[3], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B017", "name": "Control panel / VFD", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B018", "name": "Cooling water jacket / system", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B019", "name": "Level sensor (mill sump)", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B020", "name": "Grease nipples & fittings", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B021", "name": "Bolt sets / liner bolts", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B022", "name": "Shock absorber / mounts", "category": MAINTENANCE_CATEGORIES[3], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B023", "name": "Motor starter / switchgear", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "B024", "name": "Dust suppression spray system", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]}
    ],
    "Flotation Cell": [
        {"component_id": "F001", "name": "Tank / cell body", "category": MAINTENANCE_CATEGORIES[3], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F002", "name": "Impeller / agitator", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F003", "name": "Stator", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F004", "name": "Motor agitator", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F005", "name": "Air blower / compressor", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F006", "name": "Air distribution manifold", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F007", "name": "Froth paddles / skimmers", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F008", "name": "Weir plates", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F009", "name": "Level sensor", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F010", "name": "Flow meter (reagent feed)", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F011", "name": "Valve actuators", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F012", "name": "Piping & hoses", "category": MAINTENANCE_CATEGORIES[3], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F013", "name": "Chemical dosing pumps", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F014", "name": "Mixer gearbox", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F015", "name": "Bearing (agitator)", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F016", "name": "Seal kit (agitator)", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F017", "name": "Control valve (air)", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F018", "name": "Control panel / PLC", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F019", "name": "Sampling port", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "F020", "name": "Collector / frother storage tank", "category": MAINTENANCE_CATEGORIES[3], "status": COMPONENT_STATUSES[0]}
    ],
    "Smelter / Furnace": [
        {"component_id": "S001", "name": "Burner / heating element", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S002", "name": "Furnace shell / hearth", "category": MAINTENANCE_CATEGORIES[3], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S003", "name": "Refractory lining", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S004", "name": "Thermocouple(s)", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S005", "name": "Combustion air blower", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S006", "name": "Feed chute / charge feeder", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S007", "name": "Tap hole & valve", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S008", "name": "Cooling water system", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S009", "name": "Transformer / power supply", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S010", "name": "Electrodes (if electric furnace)", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S011", "name": "Flue / exhaust duct", "category": MAINTENANCE_CATEGORIES[3], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S012", "name": "Baghouse / scrubber (emissions)", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S013", "name": "Gas analyzer", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S014", "name": "Furnace door actuator", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S015", "name": "Level sensor (bath)", "category": MAINTENANCE_CATEGORIES[2], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S016", "name": "Gas burner control valve", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S017", "name": "Safety relief valve", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S018", "name": "Control panel / PLC / DCS", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S019", "name": "Heat exchanger (secondary)", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S020", "name": "Slag tap system components", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S021", "name": "Oxygen lance (if used)", "category": MAINTENANCE_CATEGORIES[1], "status": COMPONENT_STATUSES[0]},
        {"component_id": "S022", "name": "Sampling & metallurgy lab port", "category": MAINTENANCE_CATEGORIES[0], "status": COMPONENT_STATUSES[0]}
    ]
}


# -----------------------------
# 4. RUTE: DAFTAR ASET
# -----------------------------
@assets_bp.route('/')
def list_assets():
    """Menampilkan daftar semua aset."""
    try:
        all_assets = list(assets_collection.find())
    except Exception as e:
        print(f"Error fetching assets: {e}")
        all_assets = []
    return render_template('assets_list.html', assets=all_assets)


# -----------------------------
# 5. RUTE: ASET DALAM PERBAIKAN
# -----------------------------
@assets_bp.route('/under_maintenance')
def assets_under_maintenance():
    """Menampilkan aset yang sedang 'Under Maintenance'."""
    try:
        # Mengubah status filter menjadi status baru 'Under Maintenance'
        under_maintenance_assets = list(assets_collection.find({"status": "Under Maintenance"}))
    except Exception as e:
        print(f"Error fetching assets under maintenance: {e}")
        under_maintenance_assets = []
    return render_template('assets_under_maintenance.html', assets=under_maintenance_assets)

# -----------------------------
# 6. RUTE: TIM MAINTENANCE
# -----------------------------
@assets_bp.route('/maintenance_team')
def maintenance_team():
    """Menampilkan daftar tim maintenance (tanpa database)."""
    # Mengubah data untuk lebih profesional (menghilangkan deskripsi yang kurang relevan)
    team = [
        {
            "name": "Alif Scott",
            "position": "Lead Mechanical Engineer",
            "responsibility": "Pengawasan dan perencanaan pemeliharaan Crusher dan Ball Mill. Mengelola tim teknisi mekanik.",
            "contact": "alscott@company.com",
            "photo": "/static/img/al.jpeg"
        },
        {
            "name": "Emiks McC",
            "position": "Senior Electrical Engineer",
            "responsibility": "Memimpin pemeliharaan sistem kontrol, PLC, dan motor pada seluruh aset.",
            "contact": "mimi@company.com",
            "photo": "/static/img/em.jpeg"
        },
        {
            "name": "Gheff Josh",
            "position": "Maintenance Supervisor",
            "responsibility": "Bertanggung jawab atas jadwal, pelaporan KPI, dan Work Order (WO) harian.",
            "contact": "g.josh@company.com",
            "photo": "/static/img/fi.jpeg"
        },
        {
            "name": "Desta Atau",
            "position": "Maintenance Technician",
            "responsibility": "Eksekusi WO dan inspeksi rutin di lapangan untuk semua mesin proses.",
            "contact": "d.atau@company.com",
            "photo": "/static/img/de.jpeg"
        }
    ]
    return render_template('maintenance_team.html', team=team)

# -----------------------------
# 7. RUTE: TAMBAH ASET BARU
# -----------------------------
@assets_bp.route('/add', methods=['GET', 'POST'])
def add_asset():
    """Form tambah aset."""
    if request.method == 'POST':
        asset_name = request.form['asset_name']
        asset_type = request.form['asset_type']
        location = request.form['location']

        components_list = COMPONENT_TEMPLATES.get(asset_type, [])

        new_asset = {
            "asset_name": asset_name,
            "type": asset_type,
            "location": location,
            "status": "Offline",
            "image_url": MACHINE_IMAGE_URLS.get(asset_type), # Tambah URL gambar
            "monitoring_data": {},
            "total_runtime_hours": 0,
            "components": components_list
        }

        try:
            assets_collection.insert_one(new_asset)
            flash(f"✅ Aset '{asset_name}' berhasil ditambahkan!", "success")
        except Exception as e:
            print(f"Error inserting asset: {e}")
            flash("❌ Gagal menambahkan aset.", "error")

        return redirect(url_for('assets.list_assets'))

    # Menambahkan tipe aset yang tersedia ke template untuk dropdown
    available_asset_types = list(COMPONENT_TEMPLATES.keys())
    return render_template('assets_form.html', asset_types=available_asset_types)


# -----------------------------
# 8. RUTE: DETAIL ASET
# -----------------------------
@assets_bp.route('/<asset_id>')
def detail_asset(asset_id):
    """Detail aset spesifik, mengirimkan status dan kategori yang tersedia."""
    try:
        asset = assets_collection.find_one({"_id": ObjectId(asset_id)})
        if not asset:
            flash("Aset tidak ditemukan.", "error")
            return redirect(url_for('assets.list_assets'))

        relevant_schedules = list(schedules_collection.find({
            "$or": [
                {"asset_type": asset.get('type')},
                {"asset_type": "All"}
            ]
        }).sort("next_due_date", 1))
        
        # Mengirimkan CONFIGURATION ke template
        return render_template(
            'assets_detail.html', 
            asset=asset, 
            schedules=relevant_schedules,
            component_statuses=COMPONENT_STATUSES,        # Status CMMS Real
            maintenance_categories=MAINTENANCE_CATEGORIES, # Kategori PM/CM/CBM
            image_url=asset.get('image_url')
        )
    except Exception as e:
        print(f"Error fetching asset detail: {e}")
        flash("Error: ID aset tidak valid.", "error")
        return redirect(url_for('assets.list_assets'))


# -----------------------------
# 9. RUTE: UPDATE KOMPONEN (FITUR LIVE UPDATE)
# -----------------------------
@assets_bp.route('/update_component_status/<asset_id>/<component_id>', methods=['POST'])
def update_component_status(asset_id, component_id):
    """
    Memperbarui status atau kategori komponen spesifik dalam array 'components' 
    menggunakan MongoDB Positional Operator ($).
    """
    try:
        new_status = request.form.get('status')
        new_category = request.form.get('category')
        
        update_fields = {}
        
        # Cek dan tambahkan update status
        if new_status:
            # Gunakan positional operator ($) untuk memperbarui elemen yang cocok dengan kriteria
            update_fields["components.$.status"] = new_status
            
        # Cek dan tambahkan update kategori
        if new_category:
            update_fields["components.$.category"] = new_category

        if not update_fields:
            # Jika tidak ada data yang dikirim
            return jsonify({"status": "error", "message": "Tidak ada data yang dikirim."}), 400

        # Query untuk menemukan Aset dan Komponen (kriteria komponen di array)
        result = assets_collection.update_one(
            {"_id": ObjectId(asset_id), "components.component_id": component_id},
            {"$set": update_fields}
        )

        if result.modified_count == 1:
            # Tambahkan logika untuk memeriksa apakah status berubah menjadi Critical
            if new_status == "Critical (Failure)":
                 # Di sini Anda bisa menambahkan trigger untuk membuat Work Order otomatis (jika ada)
                 print(f"ALERT: Komponen {component_id} pada aset {asset_id} dalam status KRITIS.")
            
            return jsonify({"status": "success", "message": f"Komponen {component_id} berhasil diperbarui."})
        else:
            return jsonify({"status": "error", "message": "Komponen atau Aset tidak ditemukan."}), 404

    except Exception as e:
        print(f"Error updating component: {e}")
        return jsonify({"status": "error", "message": f"Gagal memperbarui komponen: {str(e)}"}), 500


# -----------------------------
# 10. RUTE: UPDATE ASET (STATUS/LOKASI UTAMA)
# -----------------------------
@assets_bp.route('/update_asset/<asset_id>', methods=['POST'])
def update_asset(asset_id):
    """Update status/lokasi aset utama."""
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
            flash("✅ Data aset berhasil diperbarui!", "success")
        else:
            flash("⚠️ Tidak ada perubahan yang dilakukan.", "info")
    except Exception as e:
        print(f"Error updating asset: {e}")
        flash("❌ Gagal memperbarui data aset.", "error")

    return redirect(url_for('assets.detail_asset', asset_id=asset_id))
