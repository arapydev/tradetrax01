import redis
import json
import time

# --- Conexión a Redis ---
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def run_oms():
    """Bucle principal del Order Management System (Suscriptor)."""
    print("🚀 Iniciando OMS (Suscriptor)...")
    
    # Nos suscribimos al canal de señales
    pubsub = redis_client.pubsub()
    pubsub.subscribe('trading_signals')
    
    print("🎧 Escuchando el canal 'trading_signals' en Redis...")
    
    while True:
        # Revisa si hay un nuevo mensaje
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            # Decodificamos el mensaje JSON
            signal_data = json.loads(message['data'])
            print(f"\n✅ ¡OMS recibió la señal! -> {signal_data}")
            print(f"   (Aquí iría la lógica para enviar la orden al bróker para la cuenta '{signal_data['account_name']}')")
        
        # Pequeña pausa para no consumir 100% de CPU
        time.sleep(0.01)

if __name__ == "__main__":
    run_oms()