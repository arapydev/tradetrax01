use serde::Deserialize;
use serde_json::json;
use sqlx::PgPool;
use std::env;

#[derive(Deserialize, Debug)]
struct SignalMessage {
    account_id: i32,
    // ... (los otros campos no necesitan cambiar)
    account_name: String,
    symbol: String,
    signal_type: String,
}

#[derive(sqlx::FromRow, Debug)]
struct Account {
    id: i32,
    name: String,
    api_key: String,
    api_secret: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🚀 Iniciando OMS en Rust...");
    dotenvy::dotenv().ok();
    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");

    let db_pool = PgPool::connect(&database_url).await?;
    println!("✅ Conexión a PostgreSQL exitosa.");

    let client = redis::Client::open("redis://127.0.0.1/")?;
    // 1. Guarda la conexión en su propia variable `con` para que no sea temporal.
    let mut con = client.get_connection()?;
    // 2. Ahora crea el pubsub a partir de `con`, que sí existe.
    let mut pubsub = con.as_pubsub();
    pubsub.subscribe("trading_signals")?;
    println!("🎧 Escuchando el canal 'trading_signals'...");

    // Creamos un cliente HTTP que podemos reutilizar
    let http_client = reqwest::Client::new();

    loop {
        let msg = pubsub.get_message()?;
        let payload: String = msg.get_payload()?;
        let signal: SignalMessage = match serde_json::from_str(&payload) {
            Ok(s) => s,
            Err(e) => {
                eprintln!("Error al decodificar JSON: {}", e);
                continue;
            }
        };

        println!("\n✅ ¡OMS recibió la señal! -> {:?}", signal);

        match sqlx::query_as::<_, Account>("SELECT id, name, api_key, api_secret FROM accounts WHERE id = $1")
            .bind(signal.account_id)
            .fetch_one(&db_pool)
            .await
        {
            Ok(acc) => {
                println!("   -> Obtenida cuenta de la BD: {}", acc.name);

                // --- Lógica para enviar la orden ---
                let broker_api_url = "https://httpbin.org/post"; // URL de prueba que nos devuelve lo que enviamos
                let order_body = json!({
                    "symbol": signal.symbol,
                    "type": signal.signal_type,
                    "size": 0.01, // Lotaje fijo por ahora
                });

                println!("   -> Enviando orden a {}...", broker_api_url);

                let response = http_client
                    .post(broker_api_url)
                    .header("X-API-KEY", &acc.api_key) // Usamos la API key de la BD
                    .json(&order_body)
                    .send()
                    .await;

                match response {
                    Ok(res) => {
                        println!("   -> ✅ Respuesta del bróker (simulado): {}", res.status());
                        // let response_body = res.text().await?;
                        // println!("   -> Cuerpo de la respuesta: {}", response_body);
                    }
                    Err(e) => {
                        eprintln!("   -> ❌ Error al enviar la orden: {}", e);
                    }
                }
            }
            Err(e) => {
                eprintln!("   -> ERROR: No se pudo encontrar la cuenta con id {} en la BD: {}", signal.account_id, e);
            }
        }
    }
}