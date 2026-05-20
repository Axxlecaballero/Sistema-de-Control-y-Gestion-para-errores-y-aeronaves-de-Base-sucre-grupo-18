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

def registrar_aeronave(sigla, horas_iniciales, fabricante="", max_horas=1000, prox_inspeccion=None):
    if prox_inspeccion is None:
        prox_inspeccion = horas_iniciales + 100.0
        
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
        cursor.execute("SELECT id_aeronave, horas_vuelo, prox_inspeccion FROM aeronaves WHERE sigla = ?", (sigla,))
        aeronave = cursor.fetchone()
        
        if aeronave:
            id_aero = aeronave["id_aeronave"]
            horas_vuelo = aeronave["horas_vuelo"]
            prox_inspeccion = aeronave["prox_inspeccion"]
            
            horas_ciclo = 100.0 - (prox_inspeccion - horas_vuelo)
            if horas_ciclo <= 0:
                return False, "No se puede inspeccionar: El contador ya está en 0 hr."
            
            # 2. Registrar la inspección en el historial
            cursor.execute("""
                INSERT INTO inspecciones (hecha_por, tipo_inspeccion, fk_aeronave)
                VALUES (?, ?, ?)
            """, (tecnico, tipo, id_aero))
            
            # 3. Actualizar la aeronave: prox_inspeccion pasa a ser horas_vuelo + 100 y estado vuelve a Operativo
            cursor.execute("""
                UPDATE aeronaves 
                SET prox_inspeccion = ?, estado = 'Operativo'
                WHERE id_aeronave = ?
            """, (horas_vuelo + 100.0, id_aero))
            
            conn.commit()
            return True, "Inspección registrada con éxito."
        return False, "Aeronave no encontrada."
    except Exception as e:
        print(f"Error al realizar inspección: {e}")
        return False, "Error interno del servidor."
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Base de datos inicializada con éxito.")

def eliminar_aeronave(sigla):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_aeronave FROM aeronaves WHERE sigla = ?", (sigla,))
        row = cursor.fetchone()
        if row:
            id_aero = row["id_aeronave"]
            cursor.execute("DELETE FROM inspecciones WHERE fk_aeronave = ?", (id_aero,))
            cursor.execute("DELETE FROM piezas WHERE fk_aeronave = ?", (id_aero,))
            cursor.execute("DELETE FROM fallas WHERE fk_aeronave = ?", (id_aero,))
            cursor.execute("DELETE FROM aeronaves WHERE id_aeronave = ?", (id_aero,))
            conn.commit()
            return True, "Aeronave eliminada correctamente."
        return False, "Aeronave no encontrada."
    except Exception as e:
        print(f"Error al eliminar aeronave: {e}")
        return False, "Error interno al eliminar."
    finally:
        conn.close()

def registrar_pieza(sigla, nombre_pieza, numero_parte, numero_serie, fabricante, horas_pieza):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_aeronave FROM aeronaves WHERE sigla = ?", (sigla,))
        aeronave = cursor.fetchone()
        if aeronave:
            id_aero = aeronave["id_aeronave"]
            cursor.execute("""
                INSERT INTO piezas (nombre_pieza, numero_parte, numero_serie, fabricante, horas_pieza, fk_aeronave)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (nombre_pieza, numero_parte, numero_serie, fabricante, horas_pieza, id_aero))
            conn.commit()
            return True, "Pieza registrada con éxito"
        return False, "Aeronave no encontrada"
    except Exception as e:
        print(f"Error al registrar pieza: {e}")
        return False, "Error interno"
    finally:
        conn.close()

def obtener_piezas_por_sigla(sigla):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id_pieza, p.nombre_pieza, p.numero_parte, p.numero_serie, p.fabricante, p.horas_pieza
        FROM piezas p
        JOIN aeronaves a ON p.fk_aeronave = a.id_aeronave
        WHERE a.sigla = ?
    """, (sigla,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def sumar_horas_pieza(id_pieza, nuevas_horas):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE piezas 
        SET horas_pieza = ROUND(horas_pieza + ?, 2)
        WHERE id_pieza = ?
    """, (nuevas_horas, id_pieza))
    conn.commit()
    conn.close()

def intercambiar_pieza_db(id_pieza, sigla_destino):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_aeronave FROM aeronaves WHERE sigla = ?", (sigla_destino,))
        aeronave = cursor.fetchone()
        if aeronave:
            id_aero_dest = aeronave["id_aeronave"]
            cursor.execute("""
                UPDATE piezas
                SET fk_aeronave = ?
                WHERE id_pieza = ?
            """, (id_aero_dest, id_pieza))
            conn.commit()
            return True, "Pieza intercambiada con éxito"
        return False, "Aeronave de destino no encontrada"
    except Exception as e:
        print(f"Error al intercambiar pieza: {e}")
        return False, "Error interno"
    finally:
        conn.close()


def registrar_falla_db(sigla, reportante, titulo, descripcion):
    """Guarda una nueva falla en la base de datos SQLite."""
    conn = sqlite3.connect("mantenimiento.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_aeronave FROM aeronaves WHERE sigla = ?", (sigla,))
        aeronave = cursor.fetchone()
        
        if aeronave:
            id_aero = aeronave["id_aeronave"]
            cursor.execute("""
                INSERT INTO fallas (fk_aeronave, descubierta_por, titulo_falla, descripcion_falla, tipo_falla)
                VALUES (?, ?, ?, ?, 'Pendiente')
            """, (id_aero, reportante, titulo, descripcion))
            conn.commit()
            return True
        return False
    except Exception as e:
        print(f"Error en registrar_falla_db: {e}")
        return False
    finally:
        conn.close()

def obtener_fallas_db():
    """Recupera todos los reportes de la base de datos."""
    conn = sqlite3.connect("mantenimiento.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT a.sigla, f.descubierta_por as reportante, f.titulo_falla as falla, f.tipo_falla as status
            FROM fallas f
            JOIN aeronaves a ON f.fk_aeronave = a.id_aeronave
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error en obtener_fallas_db: {e}")
        return []
    finally:
        conn.close()

def actualizar_falla_db(sigla, titulo_original, inspector, titulo_nuevo, estado, pieza, razon):
    """Actualiza la falla y registra la solución."""
    conn = sqlite3.connect("mantenimiento.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        # Buscamos la falla específica
        cursor.execute("""
            UPDATE fallas 
            SET tipo_falla = ?, 
                titulo_falla = ?, 
                descripcion_falla = descripcion_falla || '\n[SOLUCIÓN POR ' || ? || ']: ' || ? || ' (Pieza: ' || ? || ')'
            WHERE fk_aeronave = (SELECT id_aeronave FROM aeronaves WHERE sigla = ?) 
            AND titulo_falla = ?
        """, (estado, titulo_nuevo, inspector, razon, pieza, sigla, titulo_original))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error DB: {e}")
        return False
    finally:
        conn.close()
