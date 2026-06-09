import sqlite3
import os
import sys

def get_db_path():
    """Retorna la ruta correcta de la base de datos.
    En modo EXE (PyInstaller): usa el directorio del ejecutable.
    En modo desarrollo: usa el directorio del script.
    """
    if getattr(sys, 'frozen', False):
        # Directorio donde está el .exe
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "mantenimiento.db")

DB_PATH = get_db_path()

def init_db():
    conn = sqlite3.connect(DB_PATH)
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
    
    # Migración: Agregar columna horas_vuelo_insp a inspecciones si no existe
    try:
        cursor.execute("ALTER TABLE inspecciones ADD COLUMN horas_vuelo_insp REAL")
    except sqlite3.OperationalError:
        pass

    # Tabla de Inspecciones de Piezas (Historial de inspección de piezas)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inspecciones_piezas (
        id_insp_pieza INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_insp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        hecha_por TEXT,
        horas_pieza_insp REAL,
        fk_pieza INTEGER,
        FOREIGN KEY (fk_pieza) REFERENCES piezas (id_pieza)
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
    conn = sqlite3.connect(DB_PATH)
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
    cursor.execute("SELECT id_aeronave, sigla, horas_vuelo as horas, fabricante, max_horas, prox_inspeccion, estado FROM aeronaves")
    aeronaves = [dict(row) for row in cursor.fetchall()]
    
    for a in aeronaves:
        cursor.execute("""
            SELECT horas_vuelo_insp 
            FROM inspecciones 
            WHERE fk_aeronave = ? AND horas_vuelo_insp IS NOT NULL 
            ORDER BY fecha_insp DESC LIMIT 1
        """, (a["id_aeronave"],))
        row = cursor.fetchone()
        a["horas_insp"] = row["horas_vuelo_insp"] if row else 0.0
        
    conn.close()
    return aeronaves

def sumar_horas_vuelo(sigla, nuevas_horas):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Actualizar horas de la aeronave
        cursor.execute("""
            UPDATE aeronaves 
            SET horas_vuelo = ROUND(horas_vuelo + ?, 2)
            WHERE sigla = ?
        """, (nuevas_horas, sigla))
        
        # 2. Actualizar automáticamente las horas de todas sus piezas asociadas
        cursor.execute("""
            UPDATE piezas 
            SET horas_pieza = ROUND(horas_pieza + ?, 2)
            WHERE fk_aeronave = (SELECT id_aeronave FROM aeronaves WHERE sigla = ?)
        """, (nuevas_horas, sigla))
        
        conn.commit()
    except Exception as e:
        print(f"Error al sumar horas de vuelo automáticas: {e}")
        conn.rollback()
    finally:
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
            
            # 2. Registrar la inspección en el historial con las horas de vuelo que ya tenía
            cursor.execute("""
                INSERT INTO inspecciones (hecha_por, tipo_inspeccion, fk_aeronave, horas_vuelo_insp)
                VALUES (?, ?, ?, ?)
            """, (tecnico, tipo, id_aero, horas_vuelo))
            
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
            
            # Eliminar el historial de inspecciones de todas las piezas asociadas a la aeronave
            cursor.execute("SELECT id_pieza FROM piezas WHERE fk_aeronave = ?", (id_aero,))
            piece_ids = [r["id_pieza"] for r in cursor.fetchall()]
            for pid in piece_ids:
                cursor.execute("DELETE FROM inspecciones_piezas WHERE fk_pieza = ?", (pid,))
                
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
    piezas = [dict(row) for row in cursor.fetchall()]
    
    for p in piezas:
        cursor.execute("""
            SELECT SUM(horas_pieza_insp) as total_insp 
            FROM inspecciones_piezas 
            WHERE fk_pieza = ?
        """, (p["id_pieza"],))
        row = cursor.fetchone()
        p["horas_insp"] = row["total_insp"] if (row and row["total_insp"] is not None) else 0.0
        
    conn.close()
    return piezas

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


def registrar_falla_db(sigla, reportante, titulo, descripcion, id_pieza=None, fecha=None):
    """Guarda una nueva falla en la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_aeronave FROM aeronaves WHERE sigla = ?", (sigla,))
        aeronave = cursor.fetchone()
        
        if aeronave:
            id_aero = aeronave["id_aeronave"]
            cursor.execute("""
                INSERT INTO fallas (fk_aeronave, descubierta_por, titulo_falla, descripcion_falla, tipo_falla, fecha_descubierta, fk_pieza)
                VALUES (?, ?, ?, ?, 'Pendiente', ?, ?)
            """, (id_aero, reportante, titulo, descripcion, fecha, id_pieza))
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
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT f.id_falla, a.sigla, f.descubierta_por as reportante, f.titulo_falla as falla,
                   f.tipo_falla as status, f.fecha_descubierta as fecha,
                   f.fk_pieza, COALESCE(p.nombre_pieza, 'Ninguna / General') as nombre_pieza
            FROM fallas f
            JOIN aeronaves a ON f.fk_aeronave = a.id_aeronave
            LEFT JOIN piezas p ON f.fk_pieza = p.id_pieza
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error en obtener_fallas_db: {e}")
        return []
    finally:
        conn.close()

def actualizar_falla_db(id_falla, inspector, titulo_nuevo, estado, pieza, razon):
    """Actualiza la falla y registra la solución."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        # Buscamos la falla específica por ID
        cursor.execute("""
            UPDATE fallas 
            SET tipo_falla = ?, 
                titulo_falla = ?, 
                descripcion_falla = descripcion_falla || '\n[SOLUCIÓN POR ' || ? || ']: ' || ? || ' (Pieza: ' || ? || ')'
            WHERE id_falla = ?
        """, (estado, titulo_nuevo, inspector, razon, pieza, id_falla))
        
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Error DB: {e}")
        return False
    finally:
        conn.close()


def obtener_estadisticas_fallas(fecha_inicio=None, fecha_fin=None):
    """Retorna fallas agrupadas por aeronave, ordenadas de mayor a menor cantidad."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        query = """
            SELECT a.sigla, COUNT(f.id_falla) as total_fallas,
                   SUM(CASE WHEN f.tipo_falla = 'Pendiente' THEN 1 ELSE 0 END) as pendientes,
                   SUM(CASE WHEN f.tipo_falla = 'Solucionado' THEN 1 ELSE 0 END) as solucionadas
            FROM fallas f
            JOIN aeronaves a ON f.fk_aeronave = a.id_aeronave
        """
        params = []
        
        if fecha_inicio and fecha_fin:
            query += " WHERE DATE(f.fecha_descubierta) BETWEEN ? AND ?"
            params.extend([fecha_inicio, fecha_fin])
        elif fecha_inicio:
            query += " WHERE DATE(f.fecha_descubierta) >= ?"
            params.append(fecha_inicio)
        elif fecha_fin:
            query += " WHERE DATE(f.fecha_descubierta) <= ?"
            params.append(fecha_fin)
        
        query += " GROUP BY a.sigla ORDER BY total_fallas DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error en obtener_estadisticas_fallas: {e}")
        return []
    finally:
        conn.close()


def obtener_fallas_por_aeronave_detalle(sigla, fecha_inicio=None, fecha_fin=None):
    """Retorna lista detallada de fallas para una aeronave específica."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        query = """
            SELECT f.titulo_falla, f.descripcion_falla, f.tipo_falla as status,
                   f.fecha_descubierta as fecha, f.descubierta_por as reportante
            FROM fallas f
            JOIN aeronaves a ON f.fk_aeronave = a.id_aeronave
            WHERE a.sigla = ?
        """
        params = [sigla]
        
        if fecha_inicio and fecha_fin:
            query += " AND DATE(f.fecha_descubierta) BETWEEN ? AND ?"
            params.extend([fecha_inicio, fecha_fin])
        elif fecha_inicio:
            query += " AND DATE(f.fecha_descubierta) >= ?"
            params.append(fecha_inicio)
        elif fecha_fin:
            query += " AND DATE(f.fecha_descubierta) <= ?"
            params.append(fecha_fin)
        
        query += " ORDER BY f.fecha_descubierta DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error en obtener_fallas_por_aeronave_detalle: {e}")
        return []
    finally:
        conn.close()

def obtener_fallas_por_pieza_en_periodo(sigla, periodo):
    """
    Retorna la cantidad de fallas por pieza de una aeronave específica en un periodo de tiempo.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        modificador_fecha = ""
        if periodo == "ultima_semana":
            modificador_fecha = "-7 days"
        elif periodo == "ultimo_mes":
            modificador_fecha = "-1 month"
        elif periodo == "ultimos_6_meses":
            modificador_fecha = "-6 months"
        elif periodo == "ultimo_anio":
            modificador_fecha = "-1 year"
        elif periodo == "ultimos_2_anios":
            modificador_fecha = "-2 years"
        elif periodo == "ultimos_6_anios":
            modificador_fecha = "-6 years"
        
        condicion_fecha = ""
        params = []
        if modificador_fecha:
            condicion_fecha = "AND f.fecha_descubierta >= date('now', ?)"
            params.append(modificador_fecha)
            
        params.append(sigla)
            
        query = f"""
            SELECT p.nombre_pieza, p.numero_parte, COUNT(f.id_falla) as total_fallas
            FROM piezas p
            LEFT JOIN fallas f ON p.id_pieza = f.fk_pieza {condicion_fecha}
            JOIN aeronaves a ON p.fk_aeronave = a.id_aeronave
            WHERE a.sigla = ?
            GROUP BY p.id_pieza
            ORDER BY total_fallas DESC
        """
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error en obtener_fallas_por_pieza_en_periodo: {e}")
        return []
    finally:
        conn.close()

def eliminar_pieza_db(id_pieza):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Se liberan las fallas asociadas a la pieza
        cursor.execute("UPDATE fallas SET fk_pieza = NULL WHERE fk_pieza = ?", (id_pieza,))
        cursor.execute("DELETE FROM inspecciones_piezas WHERE fk_pieza = ?", (id_pieza,))
        cursor.execute("DELETE FROM piezas WHERE id_pieza = ?", (id_pieza,))
        conn.commit()
        return True, "Pieza eliminada correctamente."
    except Exception as e:
        print(f"Error al eliminar pieza: {e}")
        return False, "Error interno al eliminar la pieza."
    finally:
        conn.close()

def inspeccionar_pieza_db(id_pieza, tecnico):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Obtener las horas actuales que tenía la pieza
        cursor.execute("SELECT horas_pieza FROM piezas WHERE id_pieza = ?", (id_pieza,))
        row = cursor.fetchone()
        if row:
            horas_pieza = row["horas_pieza"]
            
            # Registrar en el historial de inspecciones de piezas
            cursor.execute("""
                INSERT INTO inspecciones_piezas (hecha_por, fk_pieza, horas_pieza_insp)
                VALUES (?, ?, ?)
            """, (tecnico, id_pieza, horas_pieza))
            
            # Reiniciar las horas a 0.0
            cursor.execute("""
                UPDATE piezas 
                SET horas_pieza = 0.0
                WHERE id_pieza = ?
            """, (id_pieza,))
            conn.commit()
            return True, "Inspección de pieza registrada. Ciclo de horas reiniciado a 0 hr."
        return False, "Pieza no encontrada."
    except Exception as e:
        print(f"Error al inspeccionar pieza: {e}")
        return False, "Error interno al registrar inspección de la pieza."
    finally:
        conn.close()

