<a name="readme-top"></a>

<br />
<div align="center">

<h2 align="center">🍔 Tasty Delivery</h2>

  <p align="center">
    Tasty Delivery is a food delivery web application designed to bring delicious meals to your doorstep with just a few clicks.
    <br />
    <a href="https://github.com/sabrieltech/tastydelivery"><strong>View the Repository »</strong></a>
  </p>
</div>

## 🍕 Project Overview

Tasty Delivery is a full-stack food delivery web app that embraces modern DevOps practices. It features a responsive frontend, a containerized backend, and a MySQL database.

### Business Scenarios

1. **Display Personalized Homepage**  
   _Hey if you really love the chicken tendies..._ 🍗  
2. **Process Customer Payment**  
   _To get the chicken tendies sent to your house_ 🛵  
3. **Process Customer Refund**  
   _When all the chicken tendies are going home..._ 💸  

---

## 🛠️ Tech Stack

- **Frontend:** Vue.js  
- **Backend:** Python (Flask), Docker  
- **Database:** MySQL  
- **Dev Tools:** Docker Compose, WAMP/MAMP

---

## 📦 Getting Started

Follow these steps to run the application locally:

### Prerequisites

- Node.js & npm  
- Docker & Docker Compose  
- WAMP or MAMP  
- MySQL Server

## 📦 Getting Started

To run this application locally using Docker and npm, follow these steps:

1. **Make sure you have Docker, Docker Compose, Node.js, and a local MySQL server (via WAMP or MAMP) installed on your machine.**

2. **Clone this repository to your local machine.**

   ```bash
   git clone https://github.com/sabrieltech/tastydelivery.git
   ```

3. **Start your WAMP or MAMP server.**

   Make sure your MySQL server is running and accessible.

4. **Import the MySQL database.**

   - Open **phpMyAdmin** or any MySQL client.
   - Import the SQL script:

     ```sql
     fooddelivery1.sql
     ```

5. **Install frontend dependencies.**

   ```bash
   cd food-delivery-app
   npm install
   ```

6. **Start Docker and build backend services.**

   Make sure Docker is running. Then, in a new terminal:

   ```bash
   cd /backend
   docker-compose up --build
   ```

7. **Start the frontend server.**

   In the other terminal:

   ```bash
   cd /food-delivery-app
   npm run serve
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


