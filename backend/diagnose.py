import socket
import os
import sys

def check_db():
    try:
        import psycopg2
        # Intenta conectar con los parámetros comunes
        conn = psycopg2.connect(
            dbname="sicjac",
            user="postgres",
            password="P4$$w0rd.2025",
            host="localhost",
            port="5432"
        )
        print("✅ Conexión a Base de Datos (Puerto 5432): EXITOSA")
        conn.close()
    except Exception as e:
        print(f"❌ Conexión a Base de Datos (Puerto 5432): FALLIDA - {e}")

def check_socket():
    sock_path = "/var/www/sicjac/backend/sicjac.sock"
    if os.path.exists(sock_path):
        print(f"✅ Archivo de socket existe en: {sock_path}")
        stat = os.stat(sock_path)
        print(f"   Permisos: {oct(stat.st_mode)}")
        print(f"   Propietario (UID): {stat.st_uid}")
    else:
        print(f"❌ Archivo de socket NO EXISTE en: {sock_path}")

def check_imports():
    try:
        from fastapi import FastAPI
        import uvicorn
        import gunicorn
        print("✅ Librerías base (FastAPI, Uvicorn, Gunicorn): INSTALADAS")
    except ImportError as e:
        print(f"❌ Error de Importación: {e}")

if __name__ == "__main__":
    print("--- DIAGNÓSTICO DE SICJAC BACKEND ---")
    check_imports()
    check_db()
    check_socket()
