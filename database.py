import sqlite3

def init_db():
    conn = sqlite3.connect("mantenimiento.db")
    cursor = conn.cursor()
    
    # Tabla Aeronaves (según el diagrama proporcionado)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aeronaves (
        id_aeronave INTEGER PRIMARY KEY AUTOINCREMENT,
        sigla TEXT NOT NULL UNIQUE,
        horas_vuelo REAL DEFAULT 0,
        fabricante TEXT,
        prox_inspeccion REAL,
        max_horas REAL,
        estado TEXT DEFAULT 'Operativo'
    )
    """)
    
    # Podemos crear las otras tablas del diagrama pero enfocarnos en Aeronaves por ahora
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS piezas (
        id_pieza INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_pieza TEXT,
        numero_parte TEXT,
        numero_serie TEXT,
        fabricante TEXT,
        horas_pieza REAL,
        fk_aeronave INTEGER,
        FOREIGN KEY (fk_aeronave) REFERENCES aeronaves (id_aeronave)
    )
    """)
    
    # Tabla de Inspecciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inspecciones (
        id_insp INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_insp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        hecha_por TEXT,
        tipo_inspeccion TEXT,
        fk_aeronave INTEGER,
        FOREIGN KEY (fk_aeronave) REFERENCES aeronaves (id_aeronave)
    )
    """)
    
    # Tabla de Fallas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fallas (
        id_falla INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_descubierta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tipo_falla TEXT,
        verif_criticidad BOOLEAN,
        descripcion_falla TEXT,
        descubierta_por TEXT,
        titulo_falla TEXT,
        fk_aeronave INTEGER,
        fk_pieza INTEGER,
        fk_inspeccion INTEGER,
        FOREIGN KEY (fk_aeronave) REFERENCES aeronaves (id_aeronave),
        FOREIGN KEY (fk_pieza) REFERENCES piezas (id_pieza),
        FOREIGN KEY (fk_inspeccion) REFERENCES inspecciones (id_insp)
    )
    """)
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect("mantenimiento.db")
    conn.row_factory = sqlite3.Row
    return conn

# Funciones específicas para Aeronaves (lo que pidió el usuario)

def registrar_aeronave(sigla, horas_iniciales, fabricante="", max_horas=100, prox_inspeccion=None):
    if prox_inspeccion is None:
        prox_inspeccion = horas_iniciales + max_horas
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO aeronaves (sigla, horas_vuelo, fabricante, max_horas, prox_inspeccion)
            VALUES (?, ?, ?, ?, ?)
        """, (sigla, horas_iniciales, fabricante, max_horas, prox_inspeccion))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def obtener_aeronaves():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sigla, horas_vuelo as horas, fabricante, max_horas, prox_inspeccion, estado FROM aeronaves")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def sumar_horas_vuelo(sigla, nuevas_horas):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE aeronaves 
        SET horas_vuelo = ROUND(horas_vuelo + ?, 2)
        WHERE sigla = ?
    """, (nuevas_horas, sigla))
    conn.commit()
    conn.close()

def realizar_inspeccion(sigla, tecnico, tipo="Periódica"):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Obtener datos actuales
        cursor.execute("SELECT id_aeronave, max_horas FROM aeronaves WHERE sigla = ?", (sigla,))
        aeronave = cursor.fetchone()
        
        if aeronave:
            id_aero = aeronave["id_aeronave"]
            max_h = aeronave["max_horas"]
            
            # 2. Registrar la inspección en el historial
            cursor.execute("""
                INSERT INTO inspecciones (hecha_por, tipo_inspeccion, fk_aeronave)
                VALUES (?, ?, ?)
            """, (tecnico, tipo, id_aero))
            
            # 3. Actualizar la aeronave: sumar max_horas a prox_inspeccion
            cursor.execute("""
                UPDATE aeronaves 
                SET prox_inspeccion = prox_inspeccion + ?
                WHERE id_aeronave = ?
            """, (max_h, id_aero))
            
            conn.commit()
            return True
        return False
    except Exception as e:
        print(f"Error al realizar inspección: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada con éxito.")
