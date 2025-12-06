use axum::{
    extract,
    routing::post,
    Router,
};
use sqlx::postgres::PgPoolOptions;

use serde::Deserialize;
use uuid::Uuid;

#[derive(Debug)]
#[derive(sqlx::FromRow)]
pub struct DatabaseFile {
    pub file_id: Uuid,
    pub filename: String,
    pub file_type: Option<String>,
    pub owner_id: Uuid,
    pub extension: String,
    pub size: f32,
    pub url: Option<String>,
    pub createdat: Option<String>,
    pub lastmodified: Option<String>,
    pub shared_with: Vec<String>,
}

pub async fn get_files(pool: &sqlx::PgPool, file_id: Uuid) -> Result<DatabaseFile, sqlx::Error> {
    let file = sqlx::query_as::<_, DatabaseFile>("SELECT * FROM files where file_id = $1")
        .bind(file_id)
        .fetch_one(pool)
        .await?;
    Ok(file)
}


#[tokio::main]
async fn main() {
    //postgres set up
    let database_url = "postgresql://postgres:dinqja123@localhost/servr_db"; 
    let pool = PgPoolOptions::new()
    .max_connections(5)
    .connect(&database_url)
    .await
    .expect("Failed to create pool");

    println!("Connected to the database!");
    //
    let fileID =  Uuid::parse_str("6380a4c5ff79442ca32a6eb506dd3241").unwrap();
    let file = get_files(&pool, fileID).await.unwrap();
    println!("File: {:?}", file);

    //let app = Router::new().route("/hello", get());

    //let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();

    //axum::serve(listener, app)
     //   .await
       // .unwrap();

}
