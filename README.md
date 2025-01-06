# MyUpdate
My Update to the [Group D project](https://github.com/sa-team-d) for the Smart Applications course.

**Content**

My update is to move from a query engine to a chat engine, i.e. allow follow-up questions. I implemented this update both to the local RAG (developed with LlamaIndex and Ollama) and to the RAG integrated with the interface (which uses OpenAI).

**Repository Structure:**
```
./
├── 📂 data
│   ├── 📄 costs.json 
│   ├── 📄 documentation.txt -----> new
│   ├── 📄 energies.json 
│   ├── 📄 kpi_data.json
│   ├── 📄 kpis.json -------------> new
│   ├── 📄 machine_data.json
│   ├── 📄 machines.json ---------> new
│   ├── 📄 report_data.json ------> new
│   ├── 📄 smart_app_data.pkl 
│   └── 📄 utilizations.json 
├── 📂 rag_service
│   ├── 📄 config.py
│   ├── 📄 constants.py
│   ├── 📄 prompts.py ------------> new
│   ├── 📄 rag_chat.py -----------> new
│   └── 📄 rag_lib.py
├── 📄 Chatbot_new.js ------------> new
├── 📄 Chatbot.js
├── 📄 controller_new.py ---------> new
├── 📄 controller.py
├── 📄 myupdate.ipynb ------------> new
├── 📄 rag_notebook.ipynb
└── 📄 requirements.txt
```

**Explanation of the new files**
- `documentation.txt`: new kb file with general information about the factory site
- `kpis.json`: updated version of the kb file kpi_data.json
- `machines.json`: updated version of the kb file machine_data.json
- `report_data.json`: data to generate a report with the local RAG
- `prompts.py`: updated version of the sa-team-d/rag/rag_service/constants.py file
- `rag_chat.py`: updated version of the sa-team-d/rag/rag_service/rag_lib.py file
- `Chatbot_new.js`: updated version of the sa-team-d/gui/src/components/Chatbot.js file
- `controller_new.py`: updated version of the sa-team-d/api/src/plugins/chat/controller.py file
- `myupdate.ipynb`: main notebook where I extracted the report_data file and tested the updated local RAG