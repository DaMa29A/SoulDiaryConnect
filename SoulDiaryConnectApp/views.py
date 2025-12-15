from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password, check_password
from .models import Doctor, Patient, DiaryEntry, Parameter
from llama_cpp import Llama
import logging

# Logger e Configurazione Modello
logger = logging.getLogger(__name__)
model_path = "./models/mistral/mistral-7b-v0.1.Q8_0.gguf"
# Inizializza il modello una volta sola all'avvio
try:
    llama_model = Llama(model_path=model_path, n_ctx=2048)
except Exception as e:
    logger.error(f"Errore caricamento modello Llama: {e}")
    llama_model = None

# --- VIEWS DI NAVIGAZIONE E AUTENTICAZIONE ---
def home(request):
    return render(request, 'SoulDiaryConnectApp/home.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password_input = request.POST.get('password') # Password scritta dall'utente

        # Cerca prima tra i dottori, poi tra i pazienti
        doctor = Doctor.objects.filter(email=email).first()
        patient = Patient.objects.filter(email=email).first()

        if doctor and check_password(password_input, doctor.password):
            request.session['user_type'] = 'doctor'
            request.session['user_id'] = doctor.doctor_id
            # next_url default modificato in 'doctor_home'
            next_url = request.GET.get('next', 'doctor_home') 
            return redirect(next_url)
        elif patient and check_password(password_input, patient.password):
            request.session['user_type'] = 'patient'
            request.session['user_id'] = patient.fiscal_code
            # next_url default modificato in 'patient_home'
            next_url = request.GET.get('next', 'patient_home') 
            return redirect(next_url)
        else:
            messages.error(request, 'Email o password non validi.')

    return render(request, 'SoulDiaryConnectApp/login.html')

def register_view(request):
    print("Accesso alla view di registrazione")
    if request.method == 'POST':
        try:
            user_type = request.POST.get('user_type')
            print(f"Tipo di utente selezionato: {user_type}")
            
            # Dettagli comuni
            first_name = request.POST.get('nome')
            last_name = request.POST.get('cognome')
            email = request.POST.get('email')
            #password = request.POST.get('passwd')
            raw_password = request.POST.get('passwd') # Password in chiaro

            # Controllo campi vuoti basilare
            if not first_name or not last_name or not email or not raw_password:
                messages.error(request, "Tutti i campi comuni sono obbligatori.")
                return render(request, 'SoulDiaryConnectApp/register.html')
            
            hashed_password = make_password(raw_password)

            if user_type == 'medico':
                doctor_id = request.POST.get('codice_identificativo')
                
                # Controllo se esiste già un medico con questo ID (opzionale, ma utile)
                if Doctor.objects.filter(doctor_id=doctor_id).exists():
                    messages.error(request, "Un medico con questo codice identificativo esiste già.")
                    return render(request, 'SoulDiaryConnectApp/register.html')

                Doctor.objects.create(
                    doctor_id=doctor_id,
                    first_name=first_name,
                    last_name=last_name,
                    office_address=request.POST.get('indirizzo_studio'),
                    city=request.POST.get('citta'),
                    street_number=request.POST.get('numero_civico'),
                    office_phone=request.POST.get('numero_telefono_studio'),
                    mobile_phone=request.POST.get('numero_telefono_cellulare'),
                    email=email,
                    password=hashed_password,
                )

                
            elif user_type == 'paziente':
                print("Registrazione di un paziente in corso...")
                doctor_id_input = request.POST.get('med')
                
                # Verifichiamo se il medico esiste ---
                try:
                    selected_doctor = Doctor.objects.get(doctor_id=doctor_id_input)
                except ObjectDoesNotExist:
                    messages.error(request, f"Nessun medico trovato con il codice: {doctor_id_input}")
                    return render(request, 'SoulDiaryConnectApp/register.html')
                
                Patient.objects.create(
                    fiscal_code=request.POST.get('codice_fiscale'),
                    first_name=first_name,
                    last_name=last_name,
                    birth_date=request.POST.get('data_di_nascita'),
                    doctor=selected_doctor,
                    email=email,
                    password=hashed_password,
                )

            messages.success(request, 'Registrazione completata con successo! Ora puoi effettuare il login.')
            return redirect('login')

        except IntegrityError as e:
            # Cattura errori di duplicati (Email già usata, Primary Key già usata)
            print(f"Errore Database: {e}")
            if 'email' in str(e):
                messages.error(request, "Questa email è già registrata.")
            elif 'PRIMARY' in str(e) or 'unique' in str(e):
                messages.error(request, "Il Codice Fiscale o Identificativo è già registrato.")
            else:
                messages.error(request, "Errore di integrità del database. Controlla i dati inseriti.")
            return render(request, 'SoulDiaryConnectApp/register.html')

        except Exception as e:
            # Cattura qualsiasi altro errore imprevisto
            print(f"Errore Generico: {e}") # Guarda questo nel terminale di VS Code!
            messages.error(request, f"Si è verificato un errore: {e}")
            return render(request, 'SoulDiaryConnectApp/register.html')

    print(f"Rendering registration page.")
    return render(request, 'SoulDiaryConnectApp/register.html')

def logout_view(request):
    logout(request)
    return redirect('login')

# --- DASHBOARD ---
def doctor_home(request): # Rinomina la URL in urls.py in 'doctor_home'
    if request.session.get('user_type') != 'doctor':
        return redirect('login')

    doctor_id = request.session.get('user_id')
    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)

    # Lista dei pazienti (usando il related_name 'patients')
    patients = doctor.patients.all()

    # Paziente selezionato per visualizzare le note
    selected_patient_id = request.GET.get('paziente_id')
    selected_patient = None
    diary_entries = None

    if selected_patient_id:
        selected_patient = Patient.objects.filter(fiscal_code=selected_patient_id).first()
        if selected_patient:
            diary_entries = DiaryEntry.objects.filter(patient=selected_patient).order_by('-entry_date')

    return render(request, 'SoulDiaryConnectApp/doctor_home.html', {
        'doctor': doctor,
        'patients': patients,
        'selected_patient': selected_patient,
        'diary_entries': diary_entries,
    })

def patient_home(request): # Rinomina la URL in urls.py in 'patient_home'
    if request.session.get('user_type') != 'patient':
        return redirect('login')

    patient_id = request.session.get('user_id')
    patient = get_object_or_404(Patient, fiscal_code=patient_id)
    
    # Accesso diretto al dottore grazie alla ForeignKey
    doctor = patient.doctor 

    if request.method == 'POST':
        patient_text = request.POST.get('desc')
        # generate_response_flag = request.POST.get('generateResponse') == 'on'
        
        support_text = ""
        clinical_text = ""

        if patient_text:
            # 1. Genera frase supporto
            support_text = generate_support_feedback(patient_text)

            # 2. Genera frase clinica (passando l'oggetto Doctor)
            clinical_text = generate_clinical_feedback(patient_text, doctor)

            # 3. Salva la nota (DiaryEntry)
            # Nota: Non passiamo entry_date perché è auto_now_add=True
            DiaryEntry.objects.create(
                patient=patient,
                patient_text=patient_text,
                support_text=support_text,
                clinical_text=clinical_text
            )
            
            # Pattern PRG (Post-Redirect-Get) per evitare doppio invio form
            return redirect('patient_home') 

    # Recupera le note
    diary_entries = patient.diary_entries.all().order_by('-entry_date')

    return render(request, 'SoulDiaryConnectApp/patient_home.html', {
        'patient': patient,
        'doctor': doctor,
        'diary_entries': diary_entries,
    })

# --- FUNZIONI AI (LLAMA) ---
def generate_support_feedback(text):
    print("Generating support feedback...")
    if not llama_model: return "AI Model not loaded."
    try:
        prompt = f"""
        You are a supportive assistant. Use the following example to craft your response.

        Example:
        Text: "I failed my exam and feel like giving up."
        Response: "I'm so sorry to hear about your exam. It's okay to feel disappointed, but this doesn't define your worth. 
        Consider revising your study strategy and asking for help. You've got this!"

        Now, respond to the following text:
        {text}
        """
        result = llama_model(prompt, max_tokens=150)
        return result['choices'][0]['text'].strip()
    except Exception as e:
        return f"Error generation: {e}"

def generate_clinical_feedback(text, doctor):
    print("Generating clinical feedback...")
    if not llama_model: return "AI Model not loaded."

    try:
        # 1. Imposta Max Tokens leggendo dal DOCTOR
        max_tokens = 250 if doctor.is_long else 150

        # 2. Controlla se è strutturato
        if doctor.is_structured:
            params = doctor.parameters.all()
            keys_list = [p.custom_key for p in params]
            
            if not params.exists():
                prompt = f"Analyze this text clinically: {text}"
            else:
                # Costruisce il blocco: "Key: Value"
                block = "\n".join([f"{p.custom_key}: {p.custom_value}" for p in params])
                print(f"Structured parameters block:\n{block}")
                
                prompt = f"""
                You are a psychotherapist specializing in CBT. 
                Analyze the following text and provide a clinical assessment.

                Example:
                Text: "Today I failed my exam and feel like giving up."
                Response: 
                {block}

                Parameters:
                {keys_list}
                
                Now analyze this text:
                {text}

                Respond in the format of the example response:
                """
        else:
            # Non strutturato
            prompt = f"""
            You are a psychotherapist specializing in CBT.
            Analyze the following text and provide a clinical assessment. 
            The text is: {text}
            """

        result = llama_model(prompt, max_tokens=max_tokens)
        return result['choices'][0]['text'].strip()

    except Exception as e:
        return f"Error generation: {e}"

# --- GESTIONE PARAMETRI E NOTE ---
def edit_doctor_note(request, entry_id):
    if request.method == 'POST':
        entry = get_object_or_404(DiaryEntry, id=entry_id)
        note_text = request.POST.get('doctor_note', '').strip() # Name nel form HTML deve essere doctor_note
        entry.doctor_note = note_text
        entry.save()
        return redirect(f'/doctor/home/?paziente_id={entry.patient.fiscal_code}')

def customize_generation(request):
    if request.session.get('user_type') != 'doctor':
        return redirect('login')

    doctor_id = request.session.get('user_id')
    doctor = get_object_or_404(Doctor, doctor_id=doctor_id)

    if request.method == 'POST':
        # 1. Aggiorna i flag nel modello DOCTOR
        tipo_nota = request.POST.get('tipo_nota')
        doctor.is_structured = True if tipo_nota == 'strutturato' else False

        lunghezza_nota = request.POST.get('lunghezza_nota')
        doctor.is_long = True if lunghezza_nota == 'lungo' else False
        
        doctor.save()

        # 2. Aggiorna la lista nel modello PARAMETER
        # Cancelliamo i vecchi parametri per evitare duplicati
        Parameter.objects.filter(doctor=doctor).delete()

        # Prendiamo le liste dal form (assicurati che nel HTML i name siano 'custom_key' e 'custom_value')
        keys = request.POST.getlist('custom_key')
        values = request.POST.getlist('custom_value')

        for k, v in zip(keys, values):
            if k.strip() and v.strip():
                Parameter.objects.create(doctor=doctor, custom_key=k.strip(), custom_value=v.strip())

        return redirect('doctor_home')

    # GET: Recupera i parametri esistenti
    existing_parameters = doctor.parameters.all()

    return render(request, 'SoulDiaryConnectApp/customize_generation.html', {
        'doctor': doctor,
        'existing_parameters': existing_parameters,
    })