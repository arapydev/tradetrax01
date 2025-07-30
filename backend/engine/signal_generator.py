import time
import random
import json
import redis

from ..database import SessionLocal
from ..models import Account
from sqlalchemy.orm import Session

# --- Conexión a Redis ---
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_active_accounts(db: Session) -> list[Account]:
    """Obtiene todas las cuentas activas de la base de datos."""
    return db.query(Account).filter(Account.is_active == True).all()

def get_market_data(symbol: str) -> dict:
    """Función de simulación para obtener datos de mercado."""
    price = round(random.uniform(1.05, 1.15), 5)
    print(f"  [Simulación] Precio actual de {symbol}: {price}")
    return {"price": price}

def calculate_fractal_signal(data: dict) -> str | None:
    """Función de simulación para la lógica de señales."""
    if random.randint(1, 10) == 1:
        signal = random.choice(["BUY", "SELL"])
        print(f"  🔥 ¡Señal encontrada!: {signal}")
        return signal
    return None

def run_engine():
    """Bucle principal del motor de señales."""
    print("🚀 Iniciando Signal Engine (Publicador)...")
    db = SessionLocal()
    try:
        while True:
            print("\n--- Nuevo ciclo del motor ---")
            active_accounts = get_active_accounts(db)
            
            if not active_accounts:
                print("No hay cuentas activas en la base de datos. Esperando...")
            else:
                print(f"Cuentas activas encontradas: {[acc.name for acc in active_accounts]}")
            
            for account in active_accounts:
                print(f"Procesando cuenta: '{account.name}'")
                symbol = "EURUSD"
                market_data = get_market_data(symbol)
                signal = calculate_fractal_signal(market_data)
                
                if signal:
                    # Creamos un mensaje estructurado
                    signal_message = {
                        "account_id": account.id,
                        "account_name": account.name,
                        "symbol": symbol,
                        "signal_type": signal
                    }
                    # Publicamos el mensaje en el canal 'trading_signals'
                    print(f"❗️ Publicando señal en Redis: {signal_message}")
                    redis_client.publish('trading_signals', json.dumps(signal_message))

            time.sleep(10)
    finally:
        db.close()

if __name__ == "__main__":
    run_engine()