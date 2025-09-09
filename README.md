# Inventory Management System

A web-based inventory management system built with Flask and MySQL, allowing users to manage products across multiple locations (cities), track stock movements, and maintain inventory records efficiently.

## Features

- **Location Management**: Add, view, and delete locations (cities) where inventory is stored.
- **Product Management**: Add, edit, and delete products for each location, including product names and quantities.
- **Inventory Tracking**: View all products and their quantities for a selected location.
- **Stock Movements**: Transfer products between locations, with automatic quantity updates and movement logging.
- **Movement History**: View a log of all product movements, including from/to locations, product details, and quantities.
- **Error Handling**: Built-in validation for stock availability, duplicate products, and invalid operations.
- **Responsive UI**: Clean, user-friendly interface with separate pages for different functionalities.

## Technologies Used

- **Backend**: Python Flask
- **Database**: MySQL
- **Frontend**: HTML, CSS
- **Database Connector**: mysql-connector-python

## Prerequisites

- Python 3.x installed
- MySQL Server installed and running
- Basic knowledge of command line operations

## Installation

1. **Clone the Repository**:
   ```
   git clone <repository-url>
   cd inventory-management-system
   ```

2. **Install Dependencies**:
   ```
   pip install flask mysql-connector-python
   ```

3. **Set Up the Database**:
   - Open MySQL and create a database named `inventory_management`.
   - Run the SQL queries from `db_queries.txt` to set up the required tables:
     - `Location`: Stores location names.
     - `ProductMovement`: Logs all product movements.
     - Dynamic tables for each location: `{location_name}_products` (e.g., `NewYork_products`).

## Running the Application

1. **Update Database Configuration**:
   In `app.py`, ensure the database connection details are correct:
   ```python
   db = mysql.connector.connect(
       host='localhost',
       user='root',
       password='root',
       database='inventory_management'
   )
   ```

2. **Run the Application**:
   ```
   python app.py
   ```

3. **Access the Application**:
   - Open your browser and go to `http://localhost:5000/`
   - Navigate to different sections using the menu or direct URLs.
        - http://localhost:5000/
        - http://localhost:5000/inventory
        - http://localhost:5000/locations
        - http://localhost:5000/movements

## Usage

### Home Page (`/`)
- Landing page with navigation to other sections.

### Inventory Management (`/inventory`)
- Select a location (city) from the dropdown.
- View all products for the selected location.
- Add new products: Enter product name and quantity, then click "Add Product".
- Edit existing products: Update quantity for a product.
- Delete products: Remove a product from the inventory.
- Note: Products are stored in location-specific tables (e.g., `NewYork_products`).

### Location Management (`/locations`)
- View all existing locations.
- Add a new location: Enter the location name and click "Add Location". This creates a new table for that location's products.
- Delete a location: Remove a location and its associated product table.

### Movements (`/movements`)
- View the history of all product movements.
- Each entry shows the from/to locations, product name, and quantity moved.

### Stock Transfer (`/result` - accessed via form submission)
- From the home page or inventory page, use the transfer form to move products between locations.
- Select starting location, ending location, product, and quantity.
- The system validates stock availability and updates inventories accordingly.
- View the transfer result, including before and after quantities.

## Project Structure

```
inventory-management-system/
├── app.py                          # Main Flask application
├── db_queries.txt                  # SQL queries for database setup
├── README.md                       # Project documentation
├── screenshots/                    # Screenshots of the application
├── static/                         # Static files (CSS)
│   ├── index.css
│   ├── inventory.css
│   ├── location.css
│   ├── movement.css
│   └── result.css
└── templates/                      # HTML templates
    ├── index.html
    ├── inventory.html
    ├── locations.html
    ├── movement.html
    └── result.html
```

## Screenshots

![screenshot](screenshots/01.png)