import os
from dotenv import load_dotenv
# Gunakan import yang lebih baru jika memungkinkan
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
# Impor fungsi yang sudah dimodifikasi dari elastic.py
from elastic import get_order_summary

load_dotenv()

# Inisialisasi LLM
llm = ChatOpenAI(
    temperature=0,
    model="gpt-4-0613", # Atau model lain yang Anda gunakan
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# --- Sesuaikan Deskripsi Tool untuk Fungsi Multi-Match ---
tools = [
    Tool(
        name="GetOrderSummary",
        func=get_order_summary,
        # Deskripsi baru yang sesuai dengan parameter query_string dan day
        description="Gunakan ini untuk mencari pesanan berdasarkan kata kunci umum (bisa nama pelanggan, nama produk, atau kategori produk). Anda juga bisa menambahkan filter berdasarkan hari jika disebutkan (parameter 'day'). Parameter utama adalah 'query_string'."
        # args_schema tidak digunakan di versi ini
    )
]
# --- Akhir Penyesuaian Deskripsi ---

# Pengaturan memori tetap sama
MEMORY_KEY = "chat_history"
memory = ConversationBufferMemory(memory_key=MEMORY_KEY, return_messages=True)

# Argumen agen untuk memori tetap sama
agent_kwargs = {
    "extra_prompt_messages": [MessagesPlaceholder(variable_name=MEMORY_KEY)],
}

# Inisialisasi agent executor
agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    agent_kwargs=agent_kwargs,
    memory=memory,
    handle_parsing_errors=True
)

# Fungsi chat tetap sama
def chat_with_agent(user_query: str) -> str:
    """Menjalankan query pengguna melalui agent executor."""
    try:
        # Coba gunakan .run() karena kita tidak pakai Pydantic
        # Langchain akan mencoba memetakan input ke parameter fungsi 'get_order_summary'
        response = agent_executor.run(user_query)
        # Jika .run() langsung return string
        return response
        # Jika butuh parsing output dari dict (tergantung versi Langchain & agent)
        # response_dict = agent_executor.invoke({"input": user_query})
        # output = response_dict.get("output")
        # if output is None:
        #      print(f"Agent response structure: {response_dict}")
        #      return "Maaf, terjadi format respons yang tidak terduga dari agen."
        # return output

    except Exception as e:
        print(f"Error during agent execution: {e}")
        return f"Maaf, terjadi kesalahan ({type(e).__name__}) saat memproses permintaan Anda."
