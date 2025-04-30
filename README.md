# Chatbot AI Pembelian dengan Langchain, Flask, dan Elasticsearch

Proyek ini adalah aplikasi web chatbot sederhana yang dibangun menggunakan Python, Flask, Langchain, dan Elasticsearch. Chatbot ini dirancang untuk menjawab pertanyaan pengguna terkait data pesanan (orders) dari sampel data e-commerce yang disimpan di Elasticsearch.

## Fitur Utama

* **Antarmuka Web:** Aplikasi menyediakan antarmuka web sederhana menggunakan Flask dan template HTML (`index.html`) untuk berinteraksi dengan chatbot.
* **Agen Cerdas:** Menggunakan Langchain untuk membuat agen AI (`agent.py`) yang ditenagai oleh model bahasa dari OpenAI (spesifiknya `gpt-4-0613` dalam kode ini).
* **Tool Pencarian Pesanan:** Agen dilengkapi dengan tool kustom (`GetOrderSummary`) yang berfungsi untuk mengambil data ringkasan pesanan dari Elasticsearch (`elastic.py`).
* **Kemampuan Kueri:** Berdasarkan implementasi saat ini, tool pencarian memungkinkan agen untuk mencari pesanan berdasarkan kriteria berikut:
    * Nama Pelanggan (`customer_full_name`)
    * Hari Pemesanan (`day_of_week`)
* **Responsif:** Aplikasi menampilkan pertanyaan pengguna dan jawaban dari AI di antarmuka web.

## Struktur File

* `app.py`: File utama aplikasi Flask, menangani routing dan rendering template.
* `agent.py`: Mendefinisikan agen Langchain, LLM, tools, dan logika interaksi agen.
* `elastic.py`: Berisi fungsi untuk terhubung ke Elasticsearch dan menjalankan kueri pencarian pesanan (`get_order_summary`).
* `templates/index.html`: Template HTML untuk antarmuka pengguna web.
* `requirements.txt`: Daftar dependensi Python yang diperlukan proyek.
* `.env`: (Perlu dibuat pengguna) File untuk menyimpan variabel lingkungan seperti kunci API dan kredensial Elasticsearch.

## Pengaturan dan Menjalankan

1.  **Clone Repositori:**
    ```bash
    git clone <url-repositori-anda>
    cd <nama-direktori-proyek>
    ```

2.  **Buat Virtual Environment (Direkomendasikan):**
    ```bash
    python -m venv venv
    # Aktivasi (Linux/macOS)
    source venv/bin/activate
    # Aktivasi (Windows)
    .\venv\Scripts\activate
    ```

3.  **Instal Dependensi:**
    ```bash
    pip install -r requirements.txt
    ```
    Dependensi utama meliputi: Flask, Langchain, OpenAI, Elasticsearch, python-dotenv.

4.  **Konfigurasi Environment Variables:**
    Buat file bernama `.env` di direktori utama proyek dan tambahkan variabel berikut (sesuaikan nilainya):
    ```dotenv
    OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    ELASTICSEARCH_HOST="[https://xxxxxxxxxxxx.elastic-cloud.com:9200](https://xxxxxxxxxxxx.elastic-cloud.com:9200)" # Atau host lokal Anda
    ES_USER="elastic" # Jika menggunakan autentikasi
    ES_PASSWORD="xxxxxxxxxxxxxxx" # Jika menggunakan autentikasi
    # FLASK_SECRET_KEY="kunci-rahasia-flask-anda" # Diperlukan jika menggunakan session Flask
    ```
    * Pastikan Anda memiliki akses ke indeks Elasticsearch `kibana_sample_data_ecommerce`.

5.  **Jalankan Aplikasi Flask:**
    ```bash
    python app.py
    ```
    Aplikasi akan berjalan (secara default di `http://127.0.0.1:5000`). Buka alamat tersebut di browser Anda.

## Teknologi yang Digunakan

* **Python:** Bahasa pemrograman utama.
* **Flask:** Kerangka kerja web mikro untuk backend dan penyajian HTML.
* **Langchain:** Kerangka kerja untuk membangun aplikasi berbasis LLM, digunakan untuk membuat agen dan tool.
* **OpenAI API:** Digunakan untuk mengakses model bahasa (LLM).
* **Elasticsearch:** Database NoSQL yang digunakan untuk menyimpan dan mencari data pesanan.
* **HTML/CSS:** Untuk struktur dan gaya antarmuka pengguna web.
* **Dotenv:** Untuk mengelola variabel lingkungan.

---
