from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.db import assets_collection, schedules_collection
from bson.objectid import ObjectId

# -----------------------------
# 1. DEFINISI BLUEPRINT
# -----------------------------
assets_bp = Blueprint('assets', __name__, template_folder='templates')


# -----------------------------
# 2. TEMPLATE KOMPONEN BARU
# -----------------------------
COMPONENT_TEMPLATES = {
    "Crusher": [
        {"component_id": "C001", "name": "Jaw plate", "category": "preventive", "status": "Good"},
        {"component_id": "C002", "name": "Concave / Mantle (cone)", "category": "preventive", "status": "Good"},
        {"component_id": "C003", "name": "Flywheel", "category": "corrective", "status": "Good"},
        {"component_id": "C004", "name": "Toggle plate", "category": "preventive", "status": "Good"},
        {"component_id": "C005", "name": "Eccentric shaft", "category": "corrective", "status": "Good"},
        {"component_id": "C006", "name": "Main shaft", "category": "corrective", "status": "Good"},
        {"component_id": "C007", "name": "Frame / chassis", "category": "corrective", "status": "Good"},
        {"component_id": "C008", "name": "Motor listrik utama", "category": "corrective", "status": "Good"},
        {"component_id": "C009", "name": "Coupling", "category": "preventive", "status": "Good"},
        {"component_id": "C010", "name": "Gearbox / reducer", "category": "corrective", "status": "Good"},
        {"component_id": "C011", "name": "Bearing (utama)", "category": "preventive", "status": "Good"},
        {"component_id": "C012", "name": "Lubrication pump", "category": "preventive", "status": "Good"},
        {"component_id": "C013", "name": "Oil filter", "category": "preventive", "status": "Good"},
        {"component_id": "C014", "name": "Hopper / feed chute", "category": "preventive", "status": "Good"},
        {"component_id": "C015", "name": "Feeder (vibrating feeder)", "category": "preventive", "status": "Good"},
        {"component_id": "C016", "name": "Discharge chute / grate", "category": "preventive", "status": "Good"},
        {"component_id": "C017", "name": "Belt conveyor (input)", "category": "preventive", "status": "Good"},
        {"component_id": "C018", "name": "Belt conveyor (output)", "category": "preventive", "status": "Good"},
        {"component_id": "C019", "name": "Proximity sensor (feed)", "category": "preventive", "status": "Good"},
        {"component_id": "C020", "name": "Vibration sensor (bearing)", "category": "preventive", "status": "Good"},
        {"component_id": "C021", "name": "Dust collector / baghouse connection", "category": "corrective", "status": "Good"},
        {"component_id": "C022", "name": "Control panel / PLC", "category": "corrective", "status": "Good"}
    ],

    "Ball Mill": [
        {"component_id": "B001", "name": "Drum / shell", "category": "corrective", "status": "Good"},
        {"component_id": "B002", "name": "Liner (crusher liners)", "category": "preventive", "status": "Good"},
        {"component_id": "B003", "name": "Trunnion bearing", "category": "corrective", "status": "Good"},
        {"component_id": "B004", "name": "Main bearing", "category": "preventive", "status": "Good"},
        {"component_id": "B005", "name": "Gear ring & pinion", "category": "corrective", "status": "Good"},
        {"component_id": "B006", "name": "Mill motor (ball mill drive)", "category": "corrective", "status": "Good"},
        {"component_id": "B007", "name": "Coupling & clutch", "category": "preventive", "status": "Good"},
        {"component_id": "B008", "name": "Lubrication system", "category": "preventive", "status": "Good"},
        {"component_id": "B009", "name": "Bearing temperature sensor", "category": "preventive", "status": "Good"},
        {"component_id": "B010", "name": "Vibration sensor", "category": "preventive", "status": "Good"},
        {"component_id": "B011", "name": "Feed chute / trommel feeder", "category": "preventive", "status": "Good"},
        {"component_id": "B012", "name": "Discharge grate / classifier", "category": "preventive", "status": "Good"},
        {"component_id": "B013", "name": "Grinding media (balls)", "category": "preventive", "status": "Good"},
        {"component_id": "B014", "name": "Mill speed sensor", "category": "preventive", "status": "Good"},
        {"component_id": "B015", "name": "Seals & gland", "category": "preventive", "status": "Good"},
        {"component_id": "B016", "name": "Mill foundation / baseplate", "category": "corrective", "status": "Good"},
        {"component_id": "B017", "name": "Control panel / VFD", "category": "corrective", "status": "Good"},
        {"component_id": "B018", "name": "Cooling water jacket / system", "category": "preventive", "status": "Good"},
        {"component_id": "B019", "name": "Level sensor (mill sump)", "category": "preventive", "status": "Good"},
        {"component_id": "B020", "name": "Grease nipples & fittings", "category": "preventive", "status": "Good"},
        {"component_id": "B021", "name": "Bolt sets / liner bolts", "category": "preventive", "status": "Good"},
        {"component_id": "B022", "name": "Shock absorber / mounts", "category": "preventive", "status": "Good"},
        {"component_id": "B023", "name": "Motor starter / switchgear", "category": "corrective", "status": "Good"},
        {"component_id": "B024", "name": "Dust suppression spray system", "category": "preventive", "status": "Good"}
    ],

    "Flotation Cell": [
        {"component_id": "F001", "name": "Tank / cell body", "category": "corrective", "status": "Good"},
        {"component_id": "F002", "name": "Impeller / agitator", "category": "preventive", "status": "Good"},
        {"component_id": "F003", "name": "Stator", "category": "preventive", "status": "Good"},
        {"component_id": "F004", "name": "Motor agitator", "category": "corrective", "status": "Good"},
        {"component_id": "F005", "name": "Air blower / compressor", "category": "corrective", "status": "Good"},
        {"component_id": "F006", "name": "Air distribution manifold", "category": "preventive", "status": "Good"},
        {"component_id": "F007", "name": "Froth paddles / skimmers", "category": "preventive", "status": "Good"},
        {"component_id": "F008", "name": "Weir plates", "category": "preventive", "status": "Good"},
        {"component_id": "F009", "name": "Level sensor", "category": "preventive", "status": "Good"},
        {"component_id": "F010", "name": "Flow meter (reagent feed)", "category": "preventive", "status": "Good"},
        {"component_id": "F011", "name": "Valve actuators", "category": "preventive", "status": "Good"},
        {"component_id": "F012", "name": "Piping & hoses", "category": "preventive", "status": "Good"},
        {"component_id": "F013", "name": "Chemical dosing pumps", "category": "preventive", "status": "Good"},
        {"component_id": "F014", "name": "Mixer gearbox", "category": "corrective", "status": "Good"},
        {"component_id": "F015", "name": "Bearing (agitator)", "category": "preventive", "status": "Good"},
        {"component_id": "F016", "name": "Seal kit (agitator)", "category": "preventive", "status": "Good"},
        {"component_id": "F017", "name": "Control valve (air)", "category": "preventive", "status": "Good"},
        {"component_id": "F018", "name": "Control panel / PLC", "category": "corrective", "status": "Good"},
        {"component_id": "F019", "name": "Sampling port", "category": "preventive", "status": "Good"},
        {"component_id": "F020", "name": "Collector / frother storage tank", "category": "preventive", "status": "Good"}
    ],

    "Smelter / Furnace": [
        {"component_id": "S001", "name": "Burner / heating element", "category": "corrective", "status": "Good"},
        {"component_id": "S002", "name": "Furnace shell / hearth", "category": "corrective", "status": "Good"},
        {"component_id": "S003", "name": "Refractory lining", "category": "preventive", "status": "Good"},
        {"component_id": "S004", "name": "Thermocouple(s)", "category": "preventive", "status": "Good"},
        {"component_id": "S005", "name": "Combustion air blower", "category": "corrective", "status": "Good"},
        {"component_id": "S006", "name": "Feed chute / charge feeder", "category": "preventive", "status": "Good"},
        {"component_id": "S007", "name": "Tap hole & valve", "category": "corrective", "status": "Good"},
        {"component_id": "S008", "name": "Cooling water system", "category": "preventive", "status": "Good"},
        {"component_id": "S009", "name": "Transformer / power supply", "category": "corrective", "status": "Good"},
        {"component_id": "S010", "name": "Electrodes (if electric furnace)", "category": "preventive", "status": "Good"},
        {"component_id": "S011", "name": "Flue / exhaust duct", "category": "corrective", "status": "Good"},
        {"component_id": "S012", "name": "Baghouse / scrubber (emissions)", "category": "corrective", "status": "Good"},
        {"component_id": "S013", "name": "Gas analyzer", "category": "preventive", "status": "Good"},
        {"component_id": "S014", "name": "Furnace door actuator", "category": "preventive", "status": "Good"},
        {"component_id": "S015", "name": "Level sensor (bath)", "category": "preventive", "status": "Good"},
        {"component_id": "S016", "name": "Gas burner control valve", "category": "preventive", "status": "Good"},
        {"component_id": "S017", "name": "Safety relief valve", "category": "corrective", "status": "Good"},
        {"component_id": "S018", "name": "Control panel / PLC / DCS", "category": "corrective", "status": "Good"},
        {"component_id": "S019", "name": "Heat exchanger (secondary)", "category": "corrective", "status": "Good"},
        {"component_id": "S020", "name": "Slag tap system components", "category": "preventive", "status": "Good"},
        {"component_id": "S021", "name": "Oxygen lance (if used)", "category": "corrective", "status": "Good"},
        {"component_id": "S022", "name": "Sampling & metallurgy lab port", "category": "preventive", "status": "Good"}
    ]
}


# -----------------------------
# 3. RUTE: DAFTAR ASET
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
# 4. RUTE: ASET DALAM PERBAIKAN
# -----------------------------
@assets_bp.route('/under_maintenance')
def assets_under_maintenance():
    """Menampilkan aset yang sedang 'Under Maintenance'."""
    try:
        under_maintenance_assets = list(assets_collection.find({"status": "Under Maintenance"}))
    except Exception as e:
        print(f"Error fetching assets under maintenance: {e}")
        under_maintenance_assets = []
    return render_template('assets_under_maintenance.html', assets=under_maintenance_assets)

# -----------------------------
# 4. RUTE: TIM MAINTENANCE
# -----------------------------
@assets_bp.route('/maintenance_team')
def maintenance_team():
    """Menampilkan daftar tim maintenance (tanpa database)."""
    team = [
        {
            "name": "Alif Scott",
            "position": "Bule Nyasar",
            "responsibility": "Bahas Konspirasi",
            "contact": "alscott@company.com",
            "photo": "/static/img/al.jpeg"
        },
        {
            "name": "Emiks McC",
            "position": "Electrical Engineer",
            "responsibility": "Tidur",
            "contact": "mimi@company.com",
            "photo": "/static/img/em.jpeg"
        },
        {
            "name": "Gheff Josh",
            "position": "Maintenance Supervisor",
            "responsibility": "Sibuk banget",
            "contact": "andi.pratama@company.com",
            "photo": "/static/img/fi.jpeg"
        },
        {
            "name": "Desta Atau",
            "position": "Technician",
            "responsibility": "Bingung dia juga",
            "contact": "atau@company.com",
            "photo": "/static/img/de.jpeg"
        }
    ]
    return render_template('maintenance_team.html', team=team)

# -----------------------------
# 5. RUTE: TAMBAH ASET BARU
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
            "monitoring_data": {},
            "total_runtime_hours": 0,
            "components": components_list
        }

        try:
            assets_collection.insert_one(new_asset)
            flash("✅ Aset berhasil ditambahkan!", "success")
        except Exception as e:
            print(f"Error inserting asset: {e}")
            flash("❌ Gagal menambahkan aset.", "error")

        return redirect(url_for('assets.list_assets'))

    return render_template('assets_form.html')


# -----------------------------
# 6. RUTE: DETAIL ASET
# -----------------------------
@assets_bp.route('/<asset_id>')
def detail_asset(asset_id):
    """Detail aset spesifik."""
    try:
        asset = assets_collection.find_one({"_id": ObjectId(asset_id)})
        if not asset:
            return "Aset tidak ditemukan", 404

        relevant_schedules = list(schedules_collection.find({
            "$or": [
                {"asset_type": asset['type']},
                {"asset_type": "All"}
            ]
        }).sort("next_due_date", 1))

        return render_template('assets_detail.html', asset=asset, schedules=relevant_schedules)
    except Exception as e:
        print(f"Error fetching asset detail: {e}")
        return "Error, ID aset tidak valid", 400


# -----------------------------
# 7. RUTE: UPDATE ASET
# -----------------------------
@assets_bp.route('/update_asset/<asset_id>', methods=['POST'])
def update_asset(asset_id):
    """Update status/lokasi aset."""
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


# -----------------------------
# BONUS: ALERT FLASH MESSAGE
# -----------------------------
# Di base_layout.html tambahkan:
# {% with messages = get_flashed_messages(with_categories=true) %}
#   {% if messages %}
#       {% for category, message in messages %}
#           <script>alert("{{ message }}");</script>
#       {% endfor %}
#   {% endif %}
# {% endwith %}
