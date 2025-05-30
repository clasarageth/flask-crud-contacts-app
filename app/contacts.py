from flask import Blueprint, request, render_template, redirect, url_for, flash
from db import mysql

contacts = Blueprint('contacts', __name__, template_folder='app/templates')


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
def add_contact():
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
def get_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM contacts WHERE id = %s', (id,))
    data = cur.fetchall()
    cur.close()
    return render_template('edit-contact.html', contact=data[0])


@contacts.route('/update/<id>', methods=['POST'])
def update_contact(id):
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
def delete_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM contacts WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Contact Removed Successfully')
    return redirect(url_for('contacts.Index'))


@contacts.route('/favorite/<int:id>', methods=['POST'])
def favorite_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('UPDATE contacts SET is_favorite = 1 WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Contact added to favorites')
    return redirect(url_for('contacts.Index'))


@contacts.route('/unfavorite/<int:id>', methods=['POST'])
def unfavorite_contact(id):
    cur = mysql.connection.cursor()
    cur.execute('UPDATE contacts SET is_favorite = 0 WHERE id = %s', (id,))
    mysql.connection.commit()
    flash('Contact removed from favorites')
    return redirect(url_for('contacts.Index'))
