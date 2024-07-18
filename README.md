# Fooddy

Fooddy is a Flask-based recipe application that allows users to browse, bookmark, and comment on recipes. It integrates with the Spoonacular API to fetch a variety of recipes, and it provides features for managing user accounts, bookmarking recipes, and leaving comments.

## Tech Stack I've used

I've used the following technologies in this project: Python/Flask, SQLAlchemy, Jinja, spoonacular API, HTML, Boostrap CSS.

## Live URL

Play around the app using this URL -  https://fooddy.onrender.com 


## Entity Relationship Diagram

![Entity Relationship Diagram](/static/images/database.png)

This diagram represents the structure of the database. It illustrates the relationships between different entities (tables) and their attributes.

## Installation Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment tool 

### Step-by-Step Instructions

1. **Clone the Repository**

    ```bash
    git clone https://github.com/weicheng0510/Capston-Project-1.git
    cd fooddy
    ```

2. **Create and Activate a Virtual Environment**

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. **Install the Required Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables**

    Create a `.env` file in the root directory and add the following variables:

    ```env
    SECRET_KEY=your_secret_key
    SQLALCHEMY_DATABASE_URI=sqlite:///fooddy.db
    SPOONACULAR_API_KEY=your_spoonacular_api_key
    ```

5. **Initialize the Database**

    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```

6. **Run the Application**

    ```bash
    flask run
    ```

## Usage

### Browse Recipes

Users can browse recipes fetched from the Spoonacular API by searching at the homepage.

### Bookmark Recipes

Users can bookmark their favorite recipes by clicking the bookmark icon on the recipe details page.

### Add Comments

Users can add comments to recipes on the recipe details page when log in.


## Features

- **User Authentication**: Secure user authentication using Flask-Bcrypt.
- **Recipe Browsing**: Browse a variety of recipes fetched from the Spoonacular API.
- **Bookmarking**: Bookmark favorite recipes for easy access later.
- **Commenting**: Add comments to recipe details.
- **Responsive Design**: Fully responsive design for both desktop and mobile devices.

## Contributing

We welcome contributions to Fooddy! If you'd like to contribute, please follow these guidelines:

1. Fork the repository.
2. Create a new branch for your feature or bugfix (`git checkout -b feature-name`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-name`).
6. Open a pull request.

Please ensure your code adheres to our coding standards and includes appropriate tests.

## Contact Information

Created by Wei-Yuan Cheng. If you have any questions or suggestions, feel free to reach out at [sknc1993@gmail.com].

---

Thank you for using Fooddy! We hope you find it useful and enjoyable.
