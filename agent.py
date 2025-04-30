import os
from dotenv import load_dotenv
# Impor yang diperlukan dari Langchain dan OpenAI
# Direkomendasikan menggunakan langchain_openai untuk ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentExecutor
from langchain.agents.agent_types import AgentType
# Impor untuk memori percakapan
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
# Impor fungsi tool dari elastic.py (versi multi-match)
from elastic import get_order_summary

# Muat variabel lingkungan dari file .env
load_dotenv()

# --- Inisialisasi LLM ---
# Pastikan kunci API OpenAI Anda ada di file .env
llm = ChatOpenAI(
    temperature=0, # Rendah untuk jawaban yang lebih konsisten/faktual
    model="gpt-4-0613", # Pertimbangkan model yang lebih baru jika perlu
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# --- Definisi Tools ---
# Tool ini akan menggunakan fungsi get_order_summary dari elastic.py
tools = [
    Tool(
        name="GetOrderSummary",
        func=get_order_summary,
        # Deskripsi yang sesuai dengan fungsi get_order_summary versi multi-match
        description="Gunakan ini untuk mencari pesanan berdasarkan kata kunci umum (bisa nama pelanggan, nama produk, atau kategori produk). Anda juga bisa menambahkan filter berdasarkan hari jika disebutkan (parameter 'day'). Parameter utama adalah 'query_string'."
    )
]

# --- Penambahan Memori Percakapan ---
# Kunci yang digunakan untuk menyimpan/mengakses riwayat di memori
MEMORY_KEY = "chat_history"
# Inisialisasi buffer memori, return_messages=True cocok untuk model chat
memory = ConversationBufferMemory(memory_key=MEMORY_KEY, return_messages=True)

# Definisikan agent_kwargs untuk memberi tahu agen cara menggunakan memori
# MessagesPlaceholder akan menyisipkan riwayat percakapan ke dalam prompt
agent_kwargs = {
    "extra_prompt_messages": [MessagesPlaceholder(variable_name=MEMORY_KEY)],
}
# --- Akhir Penambahan Memori ---


# --- Inisialisasi Agent Executor ---
# Menggunakan initialize_agent dengan menyertakan memori dan kwargs
agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS, # Tipe agen yang baik untuk pemanggilan fungsi/tool
    verbose=True, # Tampilkan proses internal agen untuk debugging
    agent_kwargs=agent_kwargs, # Sertakan kwargs untuk memori
    memory=memory,           # Sertakan instance memori
    handle_parsing_errors=True # Menangani error parsing jika output LLM tidak sesuai format
)

# --- Fungsi Wrapper untuk Berinteraksi dengan Agen ---
def chat_with_agent(user_query: str) -> str:
    """
    Menjalankan query pengguna melalui agent executor yang memiliki memori
    dan mengembalikan respons teks.
    """
    try:
        # Menggunakan metode .invoke (lebih baru) atau .run (lebih lama)
        # .invoke lebih disarankan karena mengembalikan dictionary yang lebih terstruktur
        response = agent_executor.invoke({"input": user_query})
        # Ekstrak output dari respons dictionary
        output = response.get("output")
        if output is None:
             print(f"Struktur respons agen tidak terduga: {response}")
             return "Maaf, terjadi format respons yang tidak terduga dari agen."
        return output

        # Alternatif jika menggunakan .run() (mungkin mengembalikan string langsung)
        # response_str = agent_executor.run(user_query)
        # return response_str

    except Exception as e:
        # Cetak error untuk debugging di sisi server/konsol
        print(f"Error saat eksekusi agen: {e}")
        # Berikan pesan error yang lebih informatif ke pengguna jika mungkin
        return f"Maaf, terjadi kesalahan ({type(e).__name__}) saat memproses permintaan Anda."
