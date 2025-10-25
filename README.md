# Deployment Guide (DigitalOcean)

This guide covers deploying updates to the Django backend and React frontend running on a DigitalOcean Droplet managed by Nginx, Daphne, and Systemd.

---

## 1. Local Preparation

* **Commit Changes:** Ensure all your code changes (both frontend and backend) are committed to your local Git repository.
    ```bash
    git add .
    git commit -m "feat: Describe your update (e.g., Add feature X, Fix bug Y)"
    ```
* **Push to GitHub:** Push your committed changes to the main branch (or your deployment branch) on GitHub.
    ```bash
    git push origin main
    ```

---

## 2. Deploy Backend Updates (on Server)

* **SSH into Server:** Connect to your DigitalOcean Droplet.
    ```bash
    ssh your_username@YOUR_DROPLET_IP_ADDRESS
    ```
* **Navigate & Activate Env:** Go to the backend directory and activate the Python virtual environment.
    ```bash
    cd ~/[4kara.com/backend](https://4kara.com/backend)
    source venv/bin/activate
    ```
* **Pull Latest Code:** Fetch the latest changes from GitHub.
    ```bash
    git pull origin main
    ```
* **Install Dependencies:** Update Python packages if `requirements.txt` changed.
    ```bash
    pip install -r requirements.txt
    ```
* **Run Migrations:** Apply any database schema changes. **(Crucial step!)**
    ```bash
    python manage.py migrate
    ```
* **Collect Static Files:** Gather updated static files for the Django admin.
    ```bash
    python manage.py collectstatic --noinput
    ```
* **Restart Application Server:** Restart Daphne (or Gunicorn if you were using it) via systemd to load the new code.
    ```bash
    sudo systemctl restart daphne.service # Or gunicorn.service
    ```
* **Check Status (Optional):** Verify the service restarted correctly.
    ```bash
    sudo systemctl status daphne.service
    ```

---

## 3. Deploy Frontend Updates (Local -> Server)

* **Build Frontend (Local):**
    * Navigate to your `frontend` directory on your **local machine**.
    * Ensure API URLs in `src/api.js` (and WebSocket URLs) point to your **production domain** (`https://4kara.com`).
    * Run the production build command:
        ```bash
        npm run build
        ```
* **Prepare Server Directory (Server):**
    * SSH into your server (if not already).
    * Temporarily give your user ownership of the web root to allow copying:
        ```bash
        sudo chown -R your_username:your_username /var/www/[4kara.com/html](https://4kara.com/html)
        ```
* **Copy Files (Local):**
    * From your **local machine's** terminal (in the project root `4kara.com`), use `scp` to copy the `build` contents:
        ```bash
        scp -r frontend/build/* your_username@YOUR_DROPLET_IP_ADDRESS:/var/www/[4kara.com/html/](https://4kara.com/html/)
        ```
* **Restore Server Permissions (Server):**
    * Switch back to your server SSH session.
    * Set ownership back to the web server user (`www-data`):
        ```bash
        sudo chown -R www-data:www-data /var/www/[4kara.com/html](https://4kara.com/html)
        ```
* **Restart Nginx (Optional but Recommended):** While not always needed for static files, restarting ensures Nginx picks up any potential config changes or clears caches.
    ```bash
    sudo systemctl restart nginx
    ```

---

## 4. Verification

* **Clear Browser Cache:** Vigorously clear your browser's cache (e.g., Ctrl+Shift+R / Cmd+Shift+R) for your site.
* **Test Live Site:** Go to `https://4kara.com` and test the updated features and ensure existing functionality still works. Check both frontend and backend interactions.

---


PROJECT

sudo chown -R sophiessa:sophiessa /var/www/4kara.com/html

sudo chown -R www-data:www-data /var/www/4kara.com/html

sudo nginx -t

sudo systemctl restart nginx

sudo systemctl restart gunicorn.service

sudo systemctl status gunicorn.service

sudo systemctl status nginx



google-oauth2: gcp

google-vertex-ai: gcp

email-vertification: sendgrid

virtual private server: digital ocean


scp -r frontend/build/* sophiessa@165.227.98.21:/var/www/4kara.com/html/