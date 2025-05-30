from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, make_response
from db import mysql

contacts = Blueprint('contacts', __name__, template_folder='app/templates')

def json_response(data, status_code=200):
    return make_response(jsonify(data), status_code)

@contacts.route('/')
def Index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts')
    data = cur.fetchall()
    cur.close()
    return render_template('index.html', contacts=data)


@contacts.route('/favorites')
def favorites():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts WHERE is_favorite = 1')
    data = cur.fetchall()
    cur.close()
    return render_template('favorites.html', contacts=data)


@contacts.route('/add_contact', methods=['POST'])
def add_contact_web():
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO contacts (fullname, phone, email, is_favorite) VALUES (%s,%s,%s,0)",
                (fullname, phone, email))
            mysql.connection.commit()
            flash('Contact Added successfully')
            return redirect(url_for('contacts.Index'))
        except Exception as e:
            flash(e.args[1])
            return redirect(url_for('contacts.Index'))


@contacts.route('/edit/<id>', methods=['POST', 'GET'])
def get_contact_web(id): 
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts WHERE id = %s', (id,))
    data = cur.fetchall()
    cur.close()
    return render_template('edit-contact.html', contact=data[0])


@contacts.route('/update/<id>', methods=['POST'])
def update_contact_web(id): 
    if request.method == 'POST':
        fullname = request.form['fullname']
        phone = request.form['phone']
        email = request.form['email']
        notes = request.form.get('notes', '')
        is_favorite = 1 if request.form.get('is_favorite') == '1' else 0
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE contacts
            SET fullname = %s,
                email = %s,
                phone = %s,
                notes = %s,
                is_favorite = %s
            WHERE id = %s
        """, (fullname, email, phone, notes, is_favorite, id))
        flash('Contact Updated Successfully')
        mysql.connection.commit()
        return redirect(url_for('contacts.Index'))


@contacts.route('/delete/<string:id>', methods=['POST', 'GET'])
def delete_contact_web(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contacts WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('contacts.Index'))


@contacts.route('/favorite/<int:id>', methods=['POST'])
def favorite_contact_web(id):
    cur = mysql.connection.cursor()
    cur.execute('UPDATE contacts SET is_favorite = 1 WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Contact added to favorites')
    return redirect(url_for('contacts.Index'))


@contacts.route('/unfavorite/<int:id>', methods=['POST'])
def unfavorite_contact_web(id):
    cur = mysql.connection.cursor()
    cur.execute('UPDATE contacts SET is_favorite = 0 WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Contact removed from favorites')
    return redirect(url_for('contacts.Index'))


@contacts.route('/api/contacts', methods=['GET'])
def api_get_all_contacts():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT id, fullname, phone, email, notes, is_favorite FROM contacts')
        data = cur.fetchall()
        cur.close()
        return json_response({"contacts": data})
    except Exception as e:
        return json_response({"message": str(e)}, 500)


@contacts.route('/api/contacts/favorites', methods=['GET'])
def api_get_favorite_contacts():
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT id, fullname, phone, email, notes, is_favorite FROM contacts WHERE is_favorite = 1')
        data = cur.fetchall()
        cur.close()
        return json_response({"favorites": data})
    except Exception as e:
        return json_response({"message": str(e)}, 500)


@contacts.route('/api/contacts', methods=['POST'])
def api_add_contact():
    data = request.get_json(silent=True)
    if data is None:
        return json_response({"message": "Invalid JSON"}, 400)

    fullname = data.get('fullname')
    phone = data.get('phone')
    email = data.get('email')
    notes = data.get('notes', '')
    is_favorite = data.get('is_favorite', 0)

    if not all([fullname, phone, email]):
        return json_response({"message": "Missing required fields: fullname, phone, and email are required."}, 400)

    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO contacts (fullname, phone, email, notes, is_favorite) VALUES (%s, %s, %s, %s, %s)",
            (fullname, phone, email, notes, is_favorite)
        )
        mysql.connection.commit()
        cur.execute("SELECT id, fullname, phone, email, notes, is_favorite FROM contacts WHERE id = LAST_INSERT_ID()")
        new_contact = cur.fetchone()
        cur.close()
        return json_response({"message": "Contact added successfully", "contact": new_contact}, 201)
    except Exception as e:
        return json_response({"message": str(e)}, 500)


@contacts.route('/api/contacts/<int:contact_id>', methods=['GET'])
def api_get_contact(contact_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT id, fullname, phone, email, notes, is_favorite FROM contacts WHERE id = %s', (contact_id,))
        data = cur.fetchone()
        cur.close()
        if data:
            return json_response({"contact": data})
        else:
            return json_response({"message": "Contact not found"}, 404)
    except Exception as e:
        return json_response({"message": str(e)}, 500)


@contacts.route('/api/contacts/<int:contact_id>', methods=['PUT'])
def api_update_contact(contact_id):
    data = request.get_json(silent=True)  
    if data is None:
        return json_response({"message": "Invalid JSON"}, 400)

    fullname = data.get('fullname')
    phone = data.get('phone')
    email = data.get('email')
    notes = data.get('notes', '')
    is_favorite = data.get('is_favorite', 0)

    if not all([fullname, phone, email]):
        return json_response({"message": "Missing required fields: fullname, phone, and email are required."}, 400)

    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT id FROM contacts WHERE id = %s', (contact_id,))
        if not cur.fetchone():
            cur.close()
            return json_response({"message": "Contact not found"}, 404)

        cur.execute("""
            UPDATE contacts
            SET fullname = %s,
                email = %s,
                phone = %s,
                notes = %s,
                is_favorite = %s
            WHERE id = %s
        """, (fullname, email, phone, notes, is_favorite, contact_id))
        mysql.connection.commit()

        cur.execute('SELECT id, fullname, phone, email, notes, is_favorite FROM contacts WHERE id = %s', (contact_id,))
        updated_contact = cur.fetchone()
        cur.close()
        return json_response({"message": "Contact updated successfully", "contact": updated_contact})
    except Exception as e:
        return json_response({"message": str(e)}, 500)


@contacts.route('/api/contacts/<int:contact_id>', methods=['PATCH'])
def api_partial_update_contact(contact_id):
    data = request.get_json(silent=True)
    if data is None:
        return json_response({"message": "Invalid JSON"}, 400)

    if isinstance(data, dict) and not data:
        return json_response({"message": "No fields to update"}, 400)

    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT fullname, phone, email, notes, is_favorite FROM contacts WHERE id = %s', (contact_id,))
        current_contact = cur.fetchone()
        if not current_contact:
            cur.close()
            return json_response({"message": "Contact not found"}, 404)

        update_fields = []
        update_values = []

        if 'fullname' in data:
            update_fields.append("fullname = %s")
            update_values.append(data['fullname'])
        if 'phone' in data:
            update_fields.append("phone = %s")
            update_values.append(data['phone'])
        if 'email' in data:
            update_fields.append("email = %s")
            update_values.append(data['email'])
        if 'notes' in data:
            update_fields.append("notes = %s")
            update_values.append(data['notes'])
        if 'is_favorite' in data:
            update_fields.append("is_favorite = %s")
            update_values.append(data['is_favorite'])

        if not update_fields:
            return json_response({"message": "No fields to update"}, 400)

        query = f"UPDATE contacts SET {', '.join(update_fields)} WHERE id = %s"
        update_values.append(contact_id)

        cur.execute(query, tuple(update_values))
        mysql.connection.commit()

        cur.execute('SELECT id, fullname, phone, email, notes, is_favorite FROM contacts WHERE id = %s', (contact_id,))
        updated_contact = cur.fetchone()
        cur.close()
        return json_response({"message": "Contact updated successfully", "contact": updated_contact})
    except Exception as e:
        return json_response({"message": str(e)}, 500)

@contacts.route('/api/contacts/<int:contact_id>', methods=['DELETE'])
def api_delete_contact(contact_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT id FROM contacts WHERE id = %s', (contact_id,))
        if not cur.fetchone():
            cur.close()
            return json_response({"message": "Contact not found"}, 404)

        cur.execute('DELETE FROM contacts WHERE id = %s', (contact_id,))
        mysql.connection.commit()
        cur.close()
        return json_response({"message": "Contact removed successfully"}, 200)
    except Exception as e:
        return json_response({"message": str(e)}, 500)


@contacts.route('/api/contacts/<int:contact_id>/favorite', methods=['POST'])
def api_favorite_contact(contact_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT id FROM contacts WHERE id = %s', (contact_id,))
        if not cur.fetchone():
            cur.close()
            return json_response({"message": "Contact not found"}, 404)

        cur.execute('UPDATE contacts SET is_favorite = 1 WHERE id = %s', (contact_id,))
        mysql.connection.commit()
        cur.close()
        return json_response({"message": "Contact added to favorites"})
    except Exception as e:
        return json_response({"message": str(e)}, 500)


@contacts.route('/api/contacts/<int:contact_id>/unfavorite', methods=['POST'])
def api_unfavorite_contact(contact_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute('SELECT id FROM contacts WHERE id = %s', (contact_id,))
        if not cur.fetchone():
            cur.close()
            return json_response({"message": "Contact not found"}, 404)

        cur.execute('UPDATE contacts SET is_favorite = 0 WHERE id = %s', (contact_id,))
        mysql.connection.commit()
        cur.close()
        return json_response({"message": "Contact removed from favorites"})
    except Exception as e:
        return json_response({"message": str(e)}, 500)