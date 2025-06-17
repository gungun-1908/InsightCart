🛍️ InsightCart
A Machine Learning–Driven E-commerce Recommendation and Analytics Platform

🧠 Overview
InsightCart is a comprehensive e-commerce analytics and recommendation system that combines machine learning, interactive dashboards, and user data collection to provide businesses with deep insights and customers with relevant product suggestions.

🔧 Features
🛒 Market Basket Analysis:
Generates product recommendations using the Apriori algorithm based on historical purchase behavior.

📊 Interactive Power BI Dashboard:
Visualizes real-time trends such as most-purchased products, category-wise engagement, and user behavior insights.

🧾 User Input Form:
Collects purchase data and preferences to drive personalized analysis.

🌐 Web Application (Flask):
Clean, functional frontend for users to input data and explore product analytics.

🛠️ Tech Stack
Area	Tools / Libraries
Programming	Python, JavaScript, HTML, CSS
Backend	Flask, SQL
ML Algorithm	Apriori (from mlxtend library)
Dashboard	Power BI
Visualization	Power BI Service
Others	Jinja Templates, Bootstrap, Pandas, NumPy

🗂️ Project Structure
InsightCart/
├── app.py                 # Flask app entry point
├── templates/
│   └── index.html         # Main frontend page
├── static/
│   └── style.css          # Custom styles
├── README.md
└── requirements.txt
🚀 How to Run
Clone the Repository

bash
Copy
Edit
git clone https://github.com/gungun-1908/InsightCart.git
cd InsightCart
Install Dependencies

bash
Copy
Edit
pip install -r requirements.txt
Run the App

bash
Copy
Edit
python app.py
View Dashboard
Open the Power BI .pbix file in Power BI Desktop or publish it to Power BI Service.


