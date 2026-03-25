import json
import os
import glob
from sqlalchemy.orm import Session
from app.models.test import Test
from app.models.test_xai import TestXAI

# LangChain and Gemini for RAG
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS

# --- Configuration ---
# User to replace this with their actual Gemini API Key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDwVpRMPFumuLVS4F_duxyGuzkBGD0m5JA")

# Paths
BASE_DIR = os.path.dirname(__file__)
DOCUMENTS_DIR = os.path.join(BASE_DIR, "..", "data", "documents")
GUIDELINES_PATH = os.path.join(BASE_DIR, "..", "data", "clinical_guidelines.json")

# Global Vector Store Cache to avoid rebuilding on every request
_VECTOR_STORE = None

def load_guidelines():
    if os.path.exists(GUIDELINES_PATH):
        with open(GUIDELINES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def get_vector_store():
    """Initializes and caches the FAISS vector store using uploaded PDFs."""
    global _VECTOR_STORE
    
    # If the default API key is still present, or missing, skip embedding to prevent crashes
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        print("WARNING: Gemini API Key not set. RAG index will not be built.")
        return None
        
    if _VECTOR_STORE is not None:
        return _VECTOR_STORE
        
    pdf_files = glob.glob(os.path.join(DOCUMENTS_DIR, "*.pdf"))
    if not pdf_files:
        print("No PDF documents found in app/data/documents/")
        return None
        
    print(f"Building RAG Index from {len(pdf_files)} PDF(s)...")
    try:
        documents = []
        for file in pdf_files:
            try:
                loader = PyPDFLoader(file)
                documents.extend(loader.load())
            except Exception as e:
                print(f"Error parsing {file}: {e}")
                
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        chunks = text_splitter.split_documents(documents)
        
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001", 
            google_api_key=GEMINI_API_KEY
        )
        _VECTOR_STORE = FAISS.from_documents(chunks, embeddings)
        print("RAG Index successfully built!")
        return _VECTOR_STORE
    except Exception as e:
        print(f"Failed to initialize vector store: {e}")
        return None

def generate_intervention_plan(db: Session, test_id: int) -> dict:
    test = db.query(Test).filter(Test.id == test_id).first()
    if not test:
        raise ValueError("Test not found")
        
    xai = db.query(TestXAI).filter(TestXAI.test_id == test_id).first()
    
    subtype = "None"
    feature_contributions = {}
    
    if xai and xai.payload_json:
        try:
            parsed = json.loads(xai.payload_json)
            if isinstance(parsed, str):
                parsed = json.loads(parsed)
            subtype = parsed.get("subtype", "None")
            feature_contributions = parsed.get("feature_contributions", {})
        except json.JSONDecodeError:
            pass
            
    # CRITICAL LOGIC FIX: Never say "Great News" if High/Moderate Risk
    final_risk = test.final_risk_label or "Unknown"
    is_at_risk = final_risk.lower() in ["high", "moderate"]
    
    guidelines = load_guidelines()
    retrieved_content = guidelines.get(subtype, {})
    general_advice = guidelines.get("General", "")
    
    if not retrieved_content and is_at_risk:
        retrieved_content = guidelines.get("Mixed_or_uncertain", {
            "title": "General Recommendations", 
            "description": "The screening indicates a complex or uncertain profile requiring careful monitoring.",
            "exercises": ["Consult an educational professional for a comprehensive assessment."]
        })

    # 1. Attempt Gemini RAG Generation
    vector_store = get_vector_store()
    
    if vector_store and is_at_risk and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
        try:
            # Retrieve relevant chunks from PDFs
            query = f"Dyslexia interventions and classroom accommodations for {subtype.replace('_', ' ')} profile and general literacy support."
            docs = vector_store.similarity_search(query, k=4)
            pdf_context = "\n\n".join([d.page_content for d in docs])
            
            prompt = f"""
You are an expert clinical educational psychologist specializing in dyslexia. 
Based on the following screening results and the provided clinical evidence from research PDFs, generate a personalized, encouraging intervention plan.

Profile Summary:
- Risk Level: {final_risk}
- Identified Profile: {subtype.replace('_', ' ')}
- Cognitive Drivers: {json.dumps(feature_contributions)}

Evidence from Clinical PDFs:
{pdf_context}

General Guidance:
{json.dumps(retrieved_content)}

Instructions:
1. Start with an empathetic 'Understanding the Profile' section explaining the risk and cognitive drivers simply.
2. Provide a 'Targeted Home Exercises' section using specific activities mentioned in the Clinical Evidence.
3. Suggest a 'School & Classroom Support' section with 3 actionable accommodations from the evidence.
4. Keep the tone professional, supportive, and free of medical jargon. Output clean Markdown.
"""
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash", 
                google_api_key=GEMINI_API_KEY, 
                temperature=0.4
            )
            response = llm.invoke(prompt)
            
            return {
                "source": "Gemini 2.5 Flash (Clinical PDF RAG)",
                "plan_markdown": response.content
            }
        except Exception as e:
            print(f"Gemini Generation Error: {e}")
            # Fall through to structured template
    
    # 2. Fallback Structured Template (Rule-Based RAG or Low Risk)
    if not is_at_risk:
        plan_markdown = "### Great News!\nNo significant dyslexia indicators were detected in this screening. Continue supporting general literacy development through regular shared reading and engaging language-rich activities at home."
    else:
        plan_markdown = f"### Understanding the Profile\nThis child has been identified with a **{final_risk}** risk level, specifically aligning with a **{subtype.replace('_', ' ')}** profile.\n\n"
        plan_markdown += f"{retrieved_content.get('description', 'A detailed clinical profile suggests focused interventions are required.')}\n\n"
        
        plan_markdown += "### Targeted Exercises\n"
        for ex in retrieved_content.get("exercises", []):
            plan_markdown += f"- {ex}\n"
            
        plan_markdown += "\n### Clinical Recommendations\n"
        plan_markdown += f"1. {general_advice}\n"
        plan_markdown += "2. Implement multisensory learning techniques (Visual, Auditory, Kinesthetic).\n"
        plan_markdown += "3. Please configure the Gemini API Key in the backend for advanced PDF-based reports.\n"
        
    return {
        "source": "Clinical Guidelines (Fallback Engine)",
        "plan_markdown": plan_markdown
    }
