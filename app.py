from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import json

app = Flask(__name__)

# --- CONEXIÓN A GOOGLE SHEETS ---
def conectar_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = json.loads(os.environ['GOOGLE_CREDENTIALS'])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

    client = gspread.authorize(creds)
    return client.open("Asistencia Colegio")  # ⚠️ nombre EXACTO

# --- ENDPOINT PRINCIPAL ---
@app.route('/asistencia', methods=['POST'])
def asistencia():
    try:
        data = request.get_json()
        dni = str(data.get("id", "")).strip()

        print("\n--- NUEVA SOLICITUD ---")
        print("DNI recibido:", dni)

        if not dni:
            return jsonify({
                "status": "error",
                "message": "DNI vacío"
            }), 400

        doc = conectar_sheets()

        hoja_docentes = doc.worksheet("Docentes")  # ⚠️ EXACTO
        hoja_asistencia = doc.worksheet("asistencia")  # ⚠️ EXACTO

        lista_dnis = hoja_docentes.col_values(1)

        print("DNIs en hoja:", lista_dnis)

        fila = None
        for i, valor in enumerate(lista_dnis, start=1):
            if valor.strip() == dni:
                fila = i
                break

        if fila is None:
            print("❌ DNI NO ENCONTRADO")
            return jsonify({
                "status": "error",
                "message": "No registrado"
            }), 404

        nombre = hoja_docentes.cell(fila, 2).value

        fecha = datetime.now(ZoneInfo("America/Argentina/Buenos_Aires")).strftime("%d/%m/%Y %H:%M:%S")
        hoja_asistencia.append_row([fecha, nombre, dni])

        print(f"✅ REGISTRADO: {nombre}")

        return jsonify({
            "status": "ok",
            "nombre": nombre
        }), 200

    except Exception as e:
        print("🔥 ERROR:", e)
        return jsonify({
            "status": "error",
            "message": "Error servidor"
        }), 500


# --- TEST ---
@app.route('/')
def home():
    return "Servidor funcionando"


# --- RUN LOCAL (Render usa gunicorn, esto es solo para pruebas) ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
