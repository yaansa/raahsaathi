\# RaahSaathi AI



\*\*Live demo (fallback mode):\*\* https://raahsaathi-1.onrender.com

The hosted version uses predefined missions because the local Gemma model can't run on a free server. Run it locally with Ollama for the full AI experience.



\## Setup

1\. Install Ollama (ollama.com)

2\. ollama pull gemma3:1b

3\. pip install fastapi uvicorn requests

4\. uvicorn app:app --reload

5\. Open http://localhost:8000



If the model is unavailable, predefined fallback missions are used.

