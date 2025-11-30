use axum::{
    extract,
    routing::post,
    Router,
};

use serde::Deserialize;

#[derive(Deserialize)]
struct File {
    file_name: String,
}

async fn hello(extract::Json(payload): extract::Json<File>) {
    println!("File name {}", payload.file_name);
}

#[tokio::main]
async fn main() {
    let app = Router::new().route("/hello", post(hello));

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();

    axum::serve(listener, app)
        .await
        .unwrap();
}
