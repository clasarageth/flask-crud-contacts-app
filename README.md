# Screenshot

![](docs/screenshot.png)

### Installation

```bash
git clone https://github.com/FaztWeb/flask-crud-contacts-app
cd flask-crud-contacts-app
pip install -r requirements.txt
python app/main.py
```

### issues
- sudo apt-get install libmysqlclient-dev

### TODO

* [ ] add authentication
* [ ] form validation
* [ ] docker-compose

# Contacts Management REST API

This project is a RESTful Contacts Management API built with Flask and MySQL. It allows users to create, read, update, and delete contact records. Additional features include support for notes and a favorites system.

## Features

### Core Features
- Add, view, update, and delete contact information
- Store the following fields: full name, phone number, email (unique)

### Notes feature (added feature)
- Add notes to any contact
- Edit or delete existing notes
- Notes are included in all relevant API responses

### Favorites feature (added feature)
- Mark or unmark contacts as favorites
- Edit favorite status using `PUT` or `PATCH`
- View favorite contacts

## Database Schema

```sql
CREATE TABLE contacts (
  id INTEGER PRIMARY KEY AUTO_INCREMENT,
  fullname VARCHAR(255),
  phone VARCHAR(255),
  email VARCHAR(255) NOT NULL UNIQUE,
  notes TEXT,
  favorite BOOLEAN DEFAULT 0
);

