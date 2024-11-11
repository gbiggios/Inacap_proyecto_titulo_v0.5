# app/utils.py
import pandas as pd
import os
from . import db
from .models import Estudiantes

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['xls', 'xlsx']

def cargar_datos_excel(filepath):
    df = pd.read_excel(filepath)
    for index, row in df.iterrows():
        nuevo_estudiante = Estudiantes(
            rut_estudiante=row['rut_estudiante'],
            nombre=row['nombre'],
            apellido_paterno=row['apellido_paterno'],
            apellido_materno=row['apellido_materno'],
            curso=row['curso'],
            correo_institucional=row['correo_institucional']
        )
        db.session.add(nuevo_estudiante)
    db.session.commit()
    os.remove(filepath)

from flask_mail import Message
from app import mail

def enviar_notificacion_suspension(taller, estudiantes, fecha_suspension):
    asunto = f"Notificación de suspensión del taller {taller.nombre}"
    cuerpo = (
        f"Estimados estudiantes,\n\n"
        f"Lamentamos informarles que el taller '{taller.nombre}', programado para el {fecha_suspension.strftime('%d-%m-%Y')}, ha sido suspendido.\n\n"
        "Saludos cordiales,\nEquipo de Administración"
    )

    # Envía un correo a cada estudiante inscrito en el taller
    for estudiante in estudiantes:
        msg = Message(
            asunto,
            recipients=[estudiante.correo_institucional],  # Asegúrate de que los estudiantes tengan un correo registrado
            body=cuerpo
        )
        mail.send(msg)
