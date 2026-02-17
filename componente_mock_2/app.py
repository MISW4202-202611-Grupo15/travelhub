from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def inicio():
    return "Hola mundo desde Flask 🚀"


@app.route("/respuesta")
def saludo():
    return "Hola, este es otro endpoint 👋"


@app.route("/usuario/<nombre>")
def usuario(nombre):
    return f"Hola {nombre}!"


@app.route("/api/producto")
def producto():
    return jsonify({"id": 1, "nombre": "Laptop", "precio": 3500})


if __name__ == "__main__":
    app.run(debug=True)
