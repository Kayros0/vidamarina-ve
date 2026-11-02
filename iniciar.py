"""Arranca Vida Marina VE en local y abre el navegador.

Pensado para el paquete de demostración: no usa el recargador de Flask y
busca un puerto libre si el 5000 está ocupado.
"""
import os
import socket
import threading
import time
import traceback
import webbrowser

from app import create_app


def _free_port(start: int = 5000) -> int:
    """Devuelve el primer puerto libre a partir de `start`."""
    for port in range(start, start + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start


def main() -> None:
    app = create_app()
    port = _free_port()
    url = f"http://127.0.0.1:{port}"

    if os.environ.get("VIDAMARINA_NO_BROWSER") != "1":
        def open_later() -> None:
            time.sleep(2)
            webbrowser.open(url)

        threading.Thread(target=open_later, daemon=True).start()

    print()
    print(f"  Vida Marina VE esta corriendo en {url}")
    print("  Cierra esta ventana o pulsa Ctrl+C para detener el servidor.")
    print()

    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
        input("\nOcurrio un error. Presiona Enter para cerrar...")
