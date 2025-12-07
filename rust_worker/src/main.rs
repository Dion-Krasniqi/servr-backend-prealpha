use axum::{
    extract,
    routing::post,
    Router,
    Json,
};
use sqlx::postgres::PgPoolOptions;

use serde::{Serialize, Deserialize};

use uuid::Uuid;
use chrono::{DateTime, Utc, NaiveDateTime};

#[derive(Deserialize)]
pub struct OwnerId {
    pub owner_id: String,
}

#[derive(Debug)]
#[derive(Serialize,sqlx::Type)]
#[sqlx(type_name = "file_type", rename_all = "lowercase")]
enum File_Type { Media, Document, Other }


use sqlx::PgPool;

#[derive(Debug)]
#[derive(Serialize, sqlx::FromRow)]
pub struct DatabaseFile {
    pub file_id: Uuid,
    pub filename: String,
    pub file_type: Option<File_Type>,
    pub owner_id: Uuid,
    pub extension: String,
    pub size: f32,
    pub url: Option<String>,
    pub createdat: Option<NaiveDateTime>,
    pub lastmodified: Option<DateTime<Utc>>,
    pub shared_with: Vec<String>,
}


async fn get_files(/*pool: &sqlx::PgPool,*/extract::State(pool): extract::State<PgPool>,
    extract::Json(payload): extract::Json<OwnerId>) -> Result<Json<Vec<DatabaseFile>>, /*sqlx::Error*/String> {

    let owner_id = match Uuid::parse_str(&payload.owner_id) {
        Ok(id) => id,
        Err(e) => return Err("Failed".to_string()),
    };

    let files = match sqlx::query_as::<_,DatabaseFile>("SELECT * FROM files where owner_id = $1")
        .bind(owner_id)
        .fetch_all(&pool)
        .await {
            Ok(f) => f,
            Err(e) => return Err(format!("Database error: {}", e)),
        };

    Ok(Json(files))
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
    
    //let ownerID =  Uuid::parse_str("50d16e49-5044-462e-afb9-63365148ac94").unwrap();

    let app = Router::new().route("/hello", post(get_files)).with_state(pool.clone());

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await.unwrap();

    axum::serve(listener, app)
        .await
        .unwrap();

}
