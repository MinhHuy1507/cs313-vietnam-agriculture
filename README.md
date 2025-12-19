<div align="center">

# Vietnam Agriculture Analytics API & Dashboard

![Streamlit Dashboard Screenshot](assets/front_dashboard.png)

<h2>Team Members</h2>


| MSSV | Name |
| :--- | :--- |
| 23520587 | Nguyễn Đức Hướng |
| 23520623 | Ngô Minh Huy |
| 23520667 | Nguyễn Hoàng Kha |
| 23520701 | Nguyễn Vũ Khang |
| 23520730 | Trương Hoàng Khiêm |
| 23520801 | Nguyễn Nghĩa Trung Kiên |
| 23520822 | Trần Tuấn Kiệt |
| 23520845 | Lê Xuân Song Lĩnh |

</div>




## 🛠️ Combined Technology Stack

| Category | Tool | Purpose |
| :--- | :--- | :--- |
| **Backend** | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white) | API server |
| | ![SQLModel](https://img.shields.io/badge/SQLModel-48B0F0?style=for-the-badge&logo=python&logoColor=white) | Database ORM & Pydantic Validation |
| **Frontend** | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white) | Interactive Dashboard UI |
| | ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white) | 2D Interactive Charts |
| | ![PyDeck](https://img.shields.io/badge/deck.gl-000000?style=for-the-badge&logo=deckdotgl&logoColor=white) | 3D Geospatial Mapping |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white) | Application Database |
| **Deployment** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) | Containerization & Local Dev |
| **Hosting** | **Render.com** | Hosting for PostgreSQL + Backend API |
| | **Streamlit Cloud** | Hosting for Frontend Dashboard |

## 📦 Running Locally (with Docker Compose)

This is the simplest way to run the entire application stack (Backend, Frontend, DB, and Seeder) on your local machine.

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

### Steps
1.  **Clone the Repository:**
    ```bash
    git clone "https://github.com/MinhHuy1507/vietnam-agriculture-app-public"
    cd vietnam-agriculture-app-public
    ```

2.  **Sync Local Database (Optional but Recommended):**
    * The `docker-compose.yml` is configured to use the user/pass `vietnamagriculture`.
    * To allow `seed_db.py` to run from your local machine (outside Docker), open `backend/utils/connect_database.py` and ensure the `_DEFAULT` variables match your local setup *or* the Docker setup (if you want to seed the Docker DB from your local terminal).

3.  **Build and Run:**
    * This command will build the `backend` and `frontend` images, start the `app-db` container, and then run the `db-seeder` job to populate the database.
    ```bash
    docker-compose build .
    docker-compose up -d
    ```

4.  **Wait for Seeder (Important):**
    * The `db-seeder` service needs about 1-2 minutes to run `seed_db.py` and populate the database. You can monitor its progress:
    ```bash
    docker-compose logs -f db-seeder
    ```
    * Wait until you see `🎉 Quá trình nạp dữ liệu mồi hoàn tất!`.

5.  **Access the Application:**
    * **Frontend (Streamlit):** [http://localhost:8501](http://localhost:8501)
    * **Backend (FastAPI Docs):** [http://localhost:8000/docs](http://localhost:8000/docs)
    * **Database (Postgres):** `localhost:5433` (Connect with DBeaver/PgAdmin using user/pass from `docker-compose.yml`)

## 📄 License
This project is licensed under the **Mozilla Public License 2.0 (MPL 2.0)**. See the `LICENSE` file for details.