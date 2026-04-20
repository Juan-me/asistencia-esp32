from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Base simple en memoria (para probar)
docentes = {
    "123": "Juan Perez",
    "456": "Maria Gomez",
    "789": "Carlos Lopez"
}

@app.route('/asistencia', methods=['POST'])
def asistencia():
    try:
        data = request.get_json()
        dni = str(data.get("id", "")).strip()

        if dni in docentes:
            nombre = docentes[dni]

            print(f"{datetime.now()} - OK - {nombre} ({dni})")

            return jsonify({
                "status": "ok",
                "nombre": nombre
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "No registrado"
            }), 404

    except Exception as e:
        print("ERROR:", e)
        return jsonify({
            "status": "error",
            "message": "Error servidor"
        }), 500


@app.route('/')
def home():
    return "Servidor funcionando"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)