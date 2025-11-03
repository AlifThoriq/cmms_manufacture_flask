from flask import Blueprint, render_template, request, redirect, url_for
from app.utils.db import inventory_collection
from bson.objectid import ObjectId

# 1. DEFINISIKAN BLUEPRINT
inventory_bp = Blueprint('inventory', __name__, template_folder='templates')


# 2. BUAT RUTE UNTUK MELIHAT DAFTAR INVENTORY (Read)
@inventory_bp.route('/')
def list_inventory():
    """Menampilkan halaman daftar semua spare part."""
    try:
        all_parts = list(inventory_collection.find())
        # Tambahkan logika cek 'low_stock'
        for part in all_parts:
            part['low_stock'] = part.get('stock_on_hand', 0) <= part.get('min_stock_level', 0)
    except Exception as e:
        print(f"Error fetching inventory: {e}")
        all_parts = []
        
    return render_template('inventory_list.html', parts=all_parts)


# 3. BUAT RUTE UNTUK MENAMBAH SPARE PART (Create)
@inventory_bp.route('/add', methods=['GET', 'POST'])
def add_part():
    """Menampilkan form untuk menambah part baru (GET) atau memproses form (POST)."""
    if request.method == 'POST':
        part_name = request.form['part_name']
        part_number = request.form['part_number']
        stock_on_hand = int(request.form['stock_on_hand'])
        min_stock_level = int(request.form['min_stock_level'])
        
        new_part = {
            "part_name": part_name,
            "part_number": part_number,
            "stock_on_hand": stock_on_hand,
            "min_stock_level": min_stock_level
        }
        
        try:
            inventory_collection.insert_one(new_part)
        except Exception as e:
            print(f"Error inserting part: {e}")
            
        return redirect(url_for('inventory.list_inventory'))

    # Jika method GET, tampilkan form
    return render_template('inventory_form.html', part=None)


# 4. BUAT RUTE UNTUK MENGEDIT SPARE PART (Update)
@inventory_bp.route('/edit/<part_id>', methods=['GET', 'POST'])
def edit_part(part_id):
    """Menampilkan form untuk mengedit part (GET) atau memproses update (POST)."""
    try:
        part = inventory_collection.find_one({"_id": ObjectId(part_id)})
        if not part:
            return "Spare part tidak ditemukan", 404

        if request.method == 'POST':
            updated_data = {
                "part_name": request.form['part_name'],
                "part_number": request.form['part_number'],
                "stock_on_hand": int(request.form['stock_on_hand']),
                "min_stock_level": int(request.form['min_stock_level'])
            }
            
            inventory_collection.update_one(
                {"_id": ObjectId(part_id)},
                {"$set": updated_data}
            )
            return redirect(url_for('inventory.list_inventory'))

        # Jika method GET, tampilkan form dengan data yang ada
        return render_template('inventory_form.html', part=part)
        
    except Exception as e:
        print(f"Error editing part: {e}")
        return "Error, ID part tidak valid", 400