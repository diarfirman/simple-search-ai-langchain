import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch, NotFoundError

load_dotenv()

# Inisialisasi koneksi Elasticsearch (sama seperti sebelumnya)
es_host = os.getenv("ELASTICSEARCH_HOST")
es_user = os.getenv("ES_USER")
es_password = os.getenv("ES_PASSWORD")

if not es_host:
    raise ValueError("ELASTICSEARCH_HOST environment variable not set.")

try:
    es = Elasticsearch(
        hosts=[es_host],
        basic_auth=(es_user, es_password) if es_user and es_password else None,
        verify_certs=True,
        request_timeout=60
    )
    if not es.ping():
        raise ConnectionError("Failed to connect to Elasticsearch.")
except Exception as e:
    raise ConnectionError(f"Error connecting to Elasticsearch: {e}") from e


# --- Fungsi Dimodifikasi: Tanpa Nested Query ---
def get_order_summary(query_string: str, day: str = None) -> str:
    """
    Mengambil ringkasan pesanan dari Elasticsearch menggunakan multi-match query
    langsung pada nama pelanggan, nama produk, dan kategori (TANPA nested query),
    dengan filter hari opsional.

    Args:
        query_string (str): Teks pencarian umum (nama, produk, kategori).
        day (str, optional): Hari dalam seminggu untuk filter tambahan. Defaults to None.

    Returns:
        str: String ringkasan pesanan yang diformat atau pesan 'tidak ditemukan'.
    """
    if not query_string:
        return "Mohon berikan kata kunci pencarian (nama pelanggan, produk, atau kategori)."

    query = {
        "size": 50,
        "query": {
            "bool": {
                "must": [
                    # --- Multi-Match Langsung (Tanpa Nested) ---
                    {
                        "multi_match": {
                            "query": query_string,
                            "fields": [
                                "customer_full_name^2", # Beri boost jika cocok nama pelanggan
                                "products.product_name",
                                "products.category"
                                # Tambahkan field lain jika perlu, misal "products.description"
                            ],
                            "type": "best_fields" # Atau tipe lain yang sesuai
                        }
                    }
                    # --- Akhir Multi-Match Langsung ---
                ],
                "filter": [] # Filter context untuk hari
            }
        }
    }

    # Tambahkan filter hari jika disediakan
    if day:
        query["query"]["bool"]["filter"].append(
            {"term": {"day_of_week": day}}
        )

    # Hapus list 'filter' jika kosong
    if not query["query"]["bool"]["filter"]:
        del query["query"]["bool"]["filter"]

    # Lakukan pencarian
    try:
        # print(f"Elasticsearch Query (Workaround): {query}") # Uncomment untuk debug
        res = es.search(index="kibana_sample_data_ecommerce", body=query)
    except NotFoundError:
        return "Error: Index 'kibana_sample_data_ecommerce' tidak ditemukan."
    except ConnectionError as e:
         print(f"Connection error during search: {e}")
         return "Maaf, terjadi masalah koneksi saat mengambil data pesanan."
    # Tangani error spesifik dari multi_match jika field tidak ada/salah mapping
    except Exception as e:
        # Periksa apakah ini error terkait field tidak ditemukan di multi_match
        if 'No keyword/text fields found' in str(e):
             print(f"Mapping Error: Pastikan field di multi_match ada dan bertipe teks/keyword. Error: {e}")
             return "Maaf, terjadi kesalahan konfigurasi pencarian. Field tidak ditemukan."
        print(f"Error searching Elasticsearch: {e}")
        print(f"Query causing error: {query}")
        return "Maaf, terjadi kesalahan tak terduga saat mengambil data pesanan."

    orders = res['hits']['hits']

    if not orders:
        return f"Tidak ditemukan pesanan yang cocok dengan '{query_string}'" + (f" pada hari '{day}'." if day else ".")

    # --- Pemformatan Output (Sama seperti sebelumnya) ---
    summary_lines = []
    order_count = 1

    criteria_str = f"yang cocok dengan '{query_string}'" + (f" pada hari {day}" if day else "")
    summary_lines.append(f"Berikut ini adalah ringkasan pembelian {criteria_str}:")

    for order in orders:
        o = order['_source']
        items = [
            f"  * {p.get('quantity', '?')}x {p.get('product_name', 'N/A')} (EUR {p.get('price', 'N/A')})"
            for p in o.get('products', [])
        ]
        items_str = "\n".join(items)

        summary_lines.append(
            f"{order_count}. Order #{o.get('order_id', 'N/A')} oleh {o.get('customer_full_name', 'N/A')} "
            f"pada {o.get('day_of_week', 'N/A')}:\n{items_str}"
        )
        order_count += 1

    return "\n".join(summary_lines)
