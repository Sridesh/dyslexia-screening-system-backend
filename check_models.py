import google.generativeai as genai

genai.configure(api_key='AIzaSyDwVpRMPFumuLVS4F_duxyGuzkBGD0m5JA')

print("Fetching available models...")
try:
    for m in genai.list_models():
        if 'embedContent' in m.supported_generation_methods:
            print(f"Embedding Model: {m.name}")
except Exception as e:
    print(f"Error: {e}")
