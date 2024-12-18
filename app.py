from flask import Flask, render_template, request, redirect
import pyodbc

app = Flask(__name__)

# Configuración de conexión a SQL Server
CONN_STR = r'DRIVER={SQL Server};SERVER=DESKTOP-LUG3D2M\SQLEXPRESS;DATABASE=Proyecto;Trusted_Connection=yes;'


# Función para obtener la conexión
def get_db():
    conn = pyodbc.connect(CONN_STR)
    return conn

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    
    # Obtener personas
    cursor.execute('SELECT * FROM Personas ORDER BY Nombre, Apellido')
    records = cursor.fetchall()
    
    # Obtener los contratos asociados a cada persona
    cursor.execute('SELECT * FROM Contrato')
    contratos = cursor.fetchall()

    conn.close()
    return render_template('index.html', records=records, contratos=contratos)

@app.route('/add', methods=['POST'])
def add_person():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        telefono = request.form['telefono']
        correo = request.form['correo']

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Personas (Nombre, Apellido, Telefono, CorreoElectronico)
                VALUES (?, ?, ?, ?)
            """, (nombre, apellido, telefono, correo))
            conn.commit()
        except Exception as e:
            print(f"Error al agregar persona: {e}")
            conn.rollback()
        conn.close()
        return redirect('/')

@app.route('/add_contract', methods=['POST'])
def add_contract():
    if request.method == 'POST':
        persona_id = request.form['persona_id']
        tipo_contrato = request.form['tipo_contrato']
        fecha_inicio = request.form['fecha_inicio']
        fecha_fin = request.form['fecha_fin']

        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Contrato (PersonaID, TipoContrato, FechaInicio, FechaFin)
                VALUES (?, ?, ?, ?)
            """, (persona_id, tipo_contrato, fecha_inicio, fecha_fin))
            conn.commit()
        except Exception as e:
            print(f"Error al agregar contrato: {e}")
            conn.rollback()
        conn.close()
        return redirect('/')

@app.route('/search', methods=['GET', 'POST'])
def search_person():
    if request.method == 'POST':
        search_term = request.form['search_term']
        search_option = request.form['search_option']

        conn = get_db()
        cursor = conn.cursor()
        
        # Consulta SQL dinámica basada en la opción de búsqueda
        query = f"""
            SELECT p.ID, p.Nombre, p.Apellido, p.Telefono, p.CorreoElectronico, c.TipoContrato, c.FechaInicio, c.FechaFin
            FROM Personas p
            LEFT JOIN Contrato c ON p.ID = c.PersonaID
            WHERE p.{search_option} LIKE ?
        """
        
        cursor.execute(query, ('%' + search_term + '%',))  # Añadimos % para realizar una búsqueda parcial
        results = cursor.fetchall()
        conn.close()

        return render_template('search.html', results=results, search_term=search_term)
    
    return render_template('search.html', results=None, search_term='')

@app.route('/delete/<int:id>', methods=['POST'])
def delete_person(id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Eliminar los contratos asociados primero
        cursor.execute("DELETE FROM Contrato WHERE PersonaID = ?", (id,))
        # Ahora eliminar la persona
        cursor.execute("DELETE FROM Personas WHERE ID = ?", (id,))
        conn.commit()
    except Exception as e:
        print(f"Error al eliminar persona: {e}")
        conn.rollback()
    conn.close()
    return redirect('/')

@app.route('/delete_contract/<int:id>', methods=['POST'])
def delete_contract(id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        # Eliminar contrato basado en el ID
        cursor.execute("DELETE FROM Contrato WHERE ID = ?", (id,))
        conn.commit()
    except Exception as e:
        print(f"Error al eliminar contrato: {e}")
        conn.rollback()
    conn.close()
    return redirect('/')

# Inicialización de la base de datos (opcional si la tabla ya está creada)
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Personas' AND xtype='U')
        CREATE TABLE Personas (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            Nombre NVARCHAR(50) NOT NULL,
            Apellido NVARCHAR(50) NOT NULL,
            Telefono NVARCHAR(20) UNIQUE NOT NULL,
            CorreoElectronico NVARCHAR(100) NULL
        )
    """)
    
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Contrato' AND xtype='U')
        CREATE TABLE Contrato (
            ID INT IDENTITY(1,1) PRIMARY KEY,
            PersonaID INT FOREIGN KEY REFERENCES Personas(ID),
            TipoContrato NVARCHAR(50),
            FechaInicio DATE,
            FechaFin DATE
        )
    """)
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()  # Inicializa la base de datos si es necesario
    app.run(debug=True, port=5002)
