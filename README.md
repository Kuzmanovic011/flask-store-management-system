# flask-store-management-system

A Flask web application for managing users, product inventory, and customer orders. Application data is stored locally in JSON files.

## Functionalities

### Authentication

- Register new users
- Sign in as an administrator or customer
- Log out securely using sessions

### Admin Panel

- View users and products
- Change user roles
- Edit product price and stock quantity
- Remove products
- View the total value of available inventory

### Customer Panel

- Browse products currently in stock
- Place product orders
- Automatically update product stock after an order
- Generate a text receipt for each order

## Technologies

- Python
- Flask
- HTML and CSS
- JSON for data storage
- Python functional tools: `map`, `filter`, and `reduce`

## How to Run

```bash
pip install flask
python app.py
```

Open the local address shown in the terminal, usually `http://127.0.0.1:5000`.
