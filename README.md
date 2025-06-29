# DataLink: A Scalable Big Data Architecture Inspired by LinkedIn

DataLink is a simulated professional networking platform inspired by LinkedIn, developed as a course project for Big Data Analytics. It showcases real-time ingestion, scalable storage, and multi-format data handling using modern open-source tools.

---

## Features

- **1M+ User Profiles** with nested education, skills, experience
- **Real-Time Interactions** via Kafka
- **MongoDB + Cassandra** for optimized big data storage
- **Media Handling** with AWS S3 (images, resumes)
- **FastAPI Backend** with RESTful endpoints
- **Streamlit Frontend** for UI interaction
- **Future-ready Analytics & Recommendation System**

---

## Tech Stack

| Category              | Tools Used                         |
|----------------------|------------------------------------|
| Data Generation      | Python (Faker)                     |
| Real-Time Ingestion  | Apache Kafka                       |
| Storage Databases    | MongoDB, Apache Cassandra          |
| Media Storage        | Amazon S3                          |
| Backend API          | FastAPI                            |
| Frontend Interface   | Streamlit                          |
| Data Formats         | JSON (nested, flat), binary (media)|

---

## Setup Instructions

1. **Clone the Repository**

    ```bash
    git clone https://github.com/mubashar-ds/data-link-app.git
    cd data-link-app
    ```

2. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3. **Start Kafka (locally or via Docker)**

    > Make sure Kafka and Zookeeper are running. You can use Docker or local installations. See [Apache Kafka Quickstart](https://kafka.apache.org/quickstart).

4. **Run Producers & Consumers**

    ```bash
    python kafka_producer.py
    python kafka_consumer.py
    ```

5. **Launch FastAPI**

    ```bash
    uvicorn backend.main:app --reload
    ```

6. **Start Streamlit UI**

    ```bash
    streamlit run streamlit_frontend.py
    ```

---

## Future Work

- Personalized job and post recommendations
- Real-time analytics dashboard using MongoDB aggregations
- Redis-based caching for faster feeds

---

## License

This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this project with proper attribution.
