\# RaahSaathi AI



Offline outdoor companion. A local open-weight model (Gemma via Ollama) gives small real-world missions for walks, nature and gardens, then turns your observations into a field note. Nothing leaves your device.



\## Setup

1\. Install Ollama (ollama.com)

2\. ollama pull gemma3:1b

3\. pip install fastapi uvicorn requests

4\. uvicorn app:app --reload

5\. Open http://localhost:8000



If the model is unavailable, predefined fallback missions are used.

