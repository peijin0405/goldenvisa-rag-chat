import streamlit as st
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.callbacks import StdOutCallbackHandler
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings, HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import PyPDFLoader
from langchain.document_loaders import UnstructuredHTMLLoader  
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
from PIL import Image



# === 引入你已有的构建函数 ===

# 构造 Prompt 模板
def build_prompt():
    return PromptTemplate.from_template(
        """
<Instructions>
You are a legal assistant specialized in immigration policies. Use only the context below to answer the question.
If the answer is not in the context, say: "No context available for this question."

Answer must include:
1. Summary of the answer in one sentence.
2. Direct quote(s) from the source document(s), if available.
3. A final conclusion in your own words.
Format your answer using clear sections: Summary, Quotes, Conclusion.
</Instructions>

<Example>
Question: 黄金签证是否允许申请人家属一同移民？
Context: 根据葡萄牙法律第23/2007号第98条第2款，申请人可以携带其配偶、未成年子女以及经济依赖的家庭成员一同申请。

Answer:
Summary:
Yes, family members can accompany the applicant.

Quotes:
- “...可以携带其配偶、未成年子女以及经济依赖的家庭成员一同申请。”

Conclusion:
The law explicitly allows family reunification under the golden visa, so applicants can include family members.
</Example>

<Example>
Question: 是否必须在葡萄牙长期居住才能保持黄金签证资格？
Context: 申请人在持有黄金签证期间，每年只需在葡萄牙境内停留7天即可维持其居留资格。

Answer:
Summary:
No, long-term residence is not required.

Quotes:
- “每年只需在葡萄牙境内停留7天即可维持其居留资格。”

Conclusion:
The golden visa program offers flexible residency requirements, making it suitable for investors who travel frequently.
</Example>

<Input>
Question: {input}
Context: {context}
Answer:
</Input>
        """
    )


# 加载向量数据库
def load_vector_store():
    embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
    return Chroma(
        persist_directory="./goldenvisa_chroma_db",
        embedding_function=embedding
    )


# 构建 Retriever（设置 k 和阈值）
def build_retriever(vector_store):
    return vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 2,
            "score_threshold": 0.1,
        },
    )

# 提取 source 信息
def format_answer_with_sources(answer: str, docs: list[Document]) -> str:
    if not docs:
        return f"{answer.strip()}\n\n📚 References:\n- No relevant source documents found."
    
    sources = "\n".join([
        f"- Source: {doc.metadata.get('source', 'N/A')}"
        for doc in docs
    ])
    return f"{answer.strip()}\n\n📚 References:\n{sources}"


# 构建带输出 & source 的增强型 RAG chain
def rag_chain():
    # 1. Load LLM
    model = ChatOllama(model="mistral")

    # 2. Prompt
    prompt = build_prompt()

    # 3. Vector store
    vector_store = load_vector_store()

    # 4. Retriever
    retriever = build_retriever(vector_store)

    # 5. Stuff chain
    document_chain = create_stuff_documents_chain(model, prompt)

    # 6. Retrieval chain
    chain = create_retrieval_chain(retriever, document_chain)

    # 7. 包装为带来源输出的执行函数
    def run_with_sources(user_input: str):
        result = chain.invoke(
            {"input": user_input},
            config={"callbacks": [StdOutCallbackHandler()]}
        )
        # 输出中包括 retrieved 文档（用于引用）
        answer = result["answer"]
        docs = result["context"]
        return format_answer_with_sources(answer, docs)

    return run_with_sources

# === Streamlit 界面 ===
# 页面设置
st.set_page_config(page_title="Portugal Golden Visa Q&A", page_icon="🌍", layout="centered")

# 设置背景颜色为图片的淡米色
st.markdown(
    """
    <style>
    body {
        background-color: #fdf7f2;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 加载头像图片
image = Image.open("assistant_avatar.png")  
st.image(image, width=120)

# 欢迎语
st.markdown("""
## 👋 Hi, I'm LusAI!
**How can I help you today?**

I’m an AI-powered assistant designed to answer your questions about the **Portugal Golden Visa** — including its requirements, benefits, application process, family migration rules, investment types, and more.
""")

# 用户输入
user_input = st.text_input("💬 Ask your question below (English or Chinese supported):", 
                           placeholder="e.g., Does the Golden Visa allow family members to immigrate?")

# 回答区域
if user_input:
    with st.spinner("Generating answer..."):
        rag_runner = rag_chain()
        answer = rag_runner(user_input)  # ✅ 直接运行并返回完整结果
        st.markdown(answer)  # ✅ 显示完整答案