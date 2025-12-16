# SoulDiaryConnect

**SoulDiaryConnect** is an AI-powered system designed to support patients in their **psychotherapeutic journey** by enabling journaling with **personalized AI feedback**, while keeping the **therapist connected and in control**. 
The platform allows patients to **log daily experiences**, receive **AI-generated motivational and clinical feedback**, and stay in touch with their physician.
The AI used is [Mistral 7B OpenOrca](https://huggingface.co/TheBloke/Mistral-7B-OpenOrca-GGUF/blob/main/mistral-7b-openorca.Q8_0.gguf).
<p align="center">
  <img src="https://github.com/FLaTNNBio/SoulDiaryConnect/blob/e029cedbdc8da70dbec7e5fe89edf20dfc26bb97/media/logo-blu.png" width="250" alt="Logo SoulDiaryConnect">
</p>

---

## Features

- **AI-Assisted Journaling** – Patients can document their daily experiences and receive **motivational feedback** from an LLM.
- **Personalized AI** – Doctors can **configure AI responses** to provide **clinical insights** and tailor support to each patient.
- **Intuitive User Interface** – A web application with **dedicated patient and doctor dashboards**.
- **Secure Data Management** – Uses **PostgreSQL** for structured data storage.
- **Advanced NLP Processing** – Powered by **Mistral-7B**, running locally with **llama_cpp**.
- **Multi-User Access** – Patients and doctors have separate roles and functionalities.

---

## Tech Stack

- **Backend**: Django
- **Frontend**: HTML, CSS, JavaScript
- **NLP**: Mistral-7B-OpenOrca-GGUF via llama_cpp
- **Database**: PostgreSQL

---

## Prerequisites
Before installing the project, make sure you have the necessary tools installed to handle AI model execution and database management.

### 1. PostgreSQL
Download and install the latest version of PostgreSQL:  
[https://www.postgresql.org/download/](https://www.postgresql.org/download/)

### 2. Local LLM Model
SoulDiaryConnect requires a local language model to operate.  
Download the following model file from Hugging Face:  
[mistral-7b-openorca.Q8_0.gguf](https://huggingface.co/TheBloke/Mistral-7B-OpenOrca-GGUF/blob/main/mistral-7b-openorca.Q8_0.gguf)

---

## Installation Guide
### **1️. Clone the repository**
```sh
git clone https://github.com/DaMa29A/SoulDiaryConnect.git
cd SoulDiaryConnect
```

### **2. Set up a virtual environment**
```sh
python3 -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
```

### **3. Install dependencies**
```sh
pip install -r requirements.txt
```


### **4. Load the NLP model**
Create the folder **models/mistral/** in the project root (if it doesn't exist).

Move the downloaded model file into **models/mistral/**.

Update the model path in **views.py** if necessary and edit the *context size* (**n_ctx** value):
```python
model_path = "./models/mistral/your_mistral-7b-openorca.Q8_0.gguf"
llama_model = Llama(model_path=model_path, n_ctx=2048)
```

### **5. Configure the database**
Create the physical database via terminal:
```sh
# Access PostgreSQL (it will ask for the password)
psql -U postgres -h localhost

# Inside the SQL shell, execute:
CREATE DATABASE souldiaryconnect_db;

# Exit the shell
\q
```

Create a file named **.env** in the main project folder and add your PostgreSQL credentials:
```sh
DB_NAME=souldiaryconnect_db
DB_USER=postgres
DB_PASSWORD=example_password
DB_HOST=localhost
DB_PORT=5432
```

Prepare and apply the database tables:
```sh
python manage.py makemigrations SoulDiaryConnectApp
python manage.py migrate
```

### **6. Start the server**
To start the application, ensure the **.venv** is active and run:
```sh
python manage.py runserver
```
The app will be available at: http://127.0.0.1:8000/

## **Roles & Functionality**
### Doctor
- **Manage patients** – Access and review patient journal entries.
- **Customize AI responses** – Configure the AI to tailor feedback generation.
- **Monitor therapy progress** – View clinical trends and intervene when necessary.
### Patient
- **Write personal journal entries** – Document daily thoughts and emotions.
- **Receive AI-generated feedback** – Get motivational and therapeutic insights.
- **View therapist's comments** – See personalized feedback from the doctor.
