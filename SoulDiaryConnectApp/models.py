from django.db import models

class Doctor(models.Model):
    doctor_id = models.CharField(max_length=12, primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    office_address = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    street_number = models.CharField(max_length=6)
    office_phone = models.CharField(max_length=13, unique=True, null=True, blank=True)
    mobile_phone = models.CharField(max_length=13, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    
    # AI Generation Settings
    is_structured = models.BooleanField(default=False)
    is_long = models.BooleanField(default=False)

    def __str__(self):
        return f"Dr. {self.last_name}"

class Parameter(models.Model):
    id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='parameters')
    custom_key = models.CharField(max_length=100)
    custom_value = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.custom_key}: {self.custom_value}"

class Patient(models.Model):
    fiscal_code = models.CharField(max_length=16, primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    birth_date = models.DateField()
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patients')
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class DiaryEntry(models.Model):
    id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='diary_entries')
    patient_text = models.TextField()
    support_text = models.TextField(null=True, blank=True)
    clinical_text = models.TextField() 
    doctor_note = models.TextField(null=True, blank=True) 
    entry_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Entry {self.entry_date} - {self.patient.last_name}"