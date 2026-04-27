# GreenField Local Hub Website

## Features

### User Roles
#
There are two main user roles:
- **Customers:** Can browse stores, add products to their cart, manage their profiles, view order history, earn/spend loyalty points, and apply coupons.
- **Sellers:** Can create and manage multiple stores, add and edit products, track store orders, update order statuses, and create store-specific promotional coupons.


### GLH Loyalty Program

Customers automatically join a loyalty program upon registration. 
  - **Earning:** 1 point earned per $1 spent.
  - **Redeeming:** 10 points = $1 discount.
  - **Tiers:** Bronze (0-499 points), Silver (500-999 points), Gold (1000+ points).
- **Coupon System:** Sellers can create discount percentage coupons. Coupons can be restricted so they are only usable by customers who have reached a specific loyalty tier (e.g., a "Gold" tier exclusive coupon).

## Prerequisites

- Python
- Django
- Pillow
```bash
pip install django
```


## Installation & Setup

1. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Django:**

   ```bash
   pip install django
   ```
3. **Install Pillow:**

    - Pillow is a python library used for image processing, required for handling product and profile images.

    ```bash
    pip install pillow
    ```

    *If a db.sqlite3 file already exists within the project, you can skip steps 4, 5 and seeding. Current db user accounts credentials are listed below.*

4. **Apply database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (Admin):**
   ```bash
   python manage.py createsuperuser
   ```
   *Note: This user will automatically be treated as a Seller when running the seed script below.*

6. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```
   Navigate to `http://127.0.0.1:8000` in your browser.

## Seeding the Database (Sample Data)

This project includes a script to easily populate your database with 10 sample stores and 50 products.

1. Open the Django interactive shell:
   ```bash
   python manage.py shell
   ```
2. Open the file `accounts/seed_data.py` in your text editor.
3. Copy the entire contents of the file.
4. Paste the copied code into the Django shell and press **Enter**.
5. Wait for the success message: `Seeding stores for user: <your_admin_user>...`
6. Type `exit()` or press `Ctrl+Z` (Windows) / `Ctrl+D` (Mac/Linux) to exit the shell.

## Project Structure

- `glh/`: The core Django project settings, WSGI/ASGI configurations, and main URL routing.
- `accounts/`: The primary app handling User authentication, Roles, Stores, Products, Carts, Orders, Loyalty Programs, and Coupons.
- `app/`: App for frontend, landing pages, or generalised site views.
- `media/`: Directory where uploaded user avatars, store logos, and product images are stored.

## Existing User Credentials

| Role | Username | Password |
| :--- | :--- | :--- |
| **Admin / Seller** | admin | secure123 |
| **Customer** | tino | secure123 |
| **Seller** | bob | secure123 |

## Builtin Django Admin
Access the Django admin interface at `http://127.0.0.1:8000/admin` using the admin account to manage users and groups.

## Custom error handling

The project includes custom views for handling common HTTP errors:
- **404 Not Found:** Displayed when a requested page or resource does not exist.
- **500 Internal Server Error:** Displayed when an unexpected server-side error occurs.

However these will only be displayed if the `DEBUG` setting in `settings.py` is set to `False`. Turning off debug mode also breaks the serving of media files in a development environment. To view the custom error pages you must switch `DEBUG = False` and then switch it back to `True` once finished testing to restore media file serving.


