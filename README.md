# E-commerce Product Manager

A simple, full-stack web application for managing e-commerce products. The application provides a clean user interface to perform CRUD (Create, Read, Update, Delete) operations on a product inventory.

The backend is built with **FastAPI** and connects to a **MySQL** database, while the frontend is built with vanilla **HTML, CSS, and JavaScript**, styled with **Tailwind CSS**.

## Features

- **View All Products**: Fetches and displays all products from the database on page load.
- **Add New Products**: A form to add new products with a name, price, stock quantity, and description.
- **Edit Products**: An interactive modal allows for updating the details of any existing product.
- **Delete Products**: Remove products from the database with a confirmation prompt.
- **Responsive UI**: The user interface is designed to work on various screen sizes.
- **Secure Credential Management**: The backend uses a `.env` file to securely manage database credentials, keeping them out of version control.

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI**: For building the high-performance REST API.
- **Uvicorn**: As the ASGI server to run the application.
- **MySQL**: As the relational database.
- **mysql-connector-python**: For connecting the Python application to the MySQL database.
- **python-dotenv**: For managing environment variables.

### Frontend
- **HTML5**
- **Vanilla JavaScript**: For all client-side logic and DOM manipulation.
- **Tailwind CSS**: For modern, utility-first styling.

## Project Structure

```
finaldatabaseweek8/
├── .env                # Stores secret environment variables (ignored by Git)
├── .gitignore          # Specifies files for Git to ignore
├── app.py              # The main FastAPI backend application
├── README.md           # This file
└── frontend/
    ├── index.html      # The main HTML file for the user interface
    ├── script.js       # Client-side JavaScript for API interaction and DOM manipulation
    └── styles.css      # Additional custom styles
```

## Setup and Installation

Follow these steps to get the application running on your local machine.

### Prerequisites

- **Python 3.11+**
- **MySQL Server**: Make sure you have a MySQL server instance running.

### 1. Clone the Repository

```bash
git clone<https://github.com/DanEinstein/E-commerce-CRUD-Operations.git>
cd finaldatabaseweek8
```

### 2. Backend Setup

a. **Create and activate a virtual environment** (recommended):

```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

b. **Install Python dependencies**:

```bash
pip install -r requirements.txt
```
*(Note: You may need to create a `requirements.txt` file first by running `pip freeze > requirements.txt`)*

c. **Create the `.env` file**:
Create a file named `.env` in the root directory and add your MySQL credentials.

```
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=ecommerce_db
```

d. **Run the backend server**:
The application will automatically create the database and tables on startup.

```bash
python -m uvicorn app:app --reload
```
The backend will be running at `http://127.0.0.1:8000`.

### 3. Frontend Setup

Simply open the `frontend/index.html` file in your web browser. The JavaScript will automatically connect to the running backend server.

## API Endpoints

The backend exposes the following RESTful API endpoints for managing products.

| Method | Endpoint                  | Description                  |
|--------|---------------------------|------------------------------|
| `GET`    | `/products`               | Get a list of all products.  |
| `POST`   | `/products`               | Create a new product.        |
| `GET`    | `/products/{product_id}`  | Get a single product by ID.  |
| `PUT`    | `/products/{product_id}`  | Update an existing product.  |
| `DELETE` | `/products/{product_id}`  | Delete a product by ID.      |

*(Similar endpoints exist for `/customers`)*

---
