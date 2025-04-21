'use strict';

// ✅ Mobile menu functionality
const mobileMenuOpenBtn = document.querySelectorAll('[data-mobile-menu-open-btn]');
const mobileMenu = document.querySelectorAll('[data-mobile-menu]');
const mobileMenuCloseBtn = document.querySelectorAll('[data-mobile-menu-close-btn]');
const overlay = document.querySelector('[data-overlay]');

for (let i = 0; i < mobileMenuOpenBtn.length; i++) {
  const mobileMenuCloseFunc = function () {
    mobileMenu[i].classList.remove('active');
    overlay.classList.remove('active');
  }

  mobileMenuOpenBtn[i].addEventListener('click', function () {
    mobileMenu[i].classList.add('active');
    overlay.classList.add('active');
  });

  mobileMenuCloseBtn[i].addEventListener('click', mobileMenuCloseFunc);
  overlay.addEventListener('click', mobileMenuCloseFunc);
}

// ✅ Accordion functionality
const accordionBtn = document.querySelectorAll('[data-accordion-btn]');
const accordion = document.querySelectorAll('[data-accordion]');

for (let i = 0; i < accordionBtn.length; i++) {
  accordionBtn[i].addEventListener('click', function () {
    const clickedBtn = this.nextElementSibling.classList.contains('active');

    for (let i = 0; i < accordion.length; i++) {
      if (clickedBtn) break;
      if (accordion[i].classList.contains('active')) {
        accordion[i].classList.remove('active');
        accordionBtn[i].classList.remove('active');
      }
    }

    this.nextElementSibling.classList.toggle('active');
    this.classList.toggle('active');
  });
}

// ✅ Toggle between registration and login forms
function toggleForms() {
  const registerForm = document.getElementById('registerForm');
  const loginForm = document.getElementById('loginForm');
  if (registerForm.style.display === "none") {
      registerForm.style.display = "block";
      loginForm.style.display = "none";
  } else {
      registerForm.style.display = "none";
      loginForm.style.display = "block";
  }
}

document.addEventListener("DOMContentLoaded", function() {
    const userFormContainer = document.getElementById("userFormContainer");
    const registerForm = document.getElementById("registerForm");
    const loginForm = document.getElementById("loginForm");

    // Open form overlay
    userFormContainer.style.display = 'block';
    document.body.style.overflow = 'hidden';

    // ✅ Handle registration
    registerForm.addEventListener("submit", function(event) {
        event.preventDefault();

        const formData = new FormData(this);
        const email = formData.get("email");

        fetch('/register', {
            method: 'POST',
            body: JSON.stringify(Object.fromEntries(formData)),
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            localStorage.setItem("userEmail", email); // ✅ Save user email
            userFormContainer.style.display = 'none';
            document.body.style.overflow = 'auto';

            // Fetch recommendations for new user
            fetchRecommendations(email);
        })
        .catch(error => alert(error.message));
    });

    // ✅ Handle login
    loginForm.addEventListener("submit", function(event) {
        event.preventDefault();

        const formData = new FormData(this);
        const email = formData.get("email");

        fetch('/login', {
            method: 'POST',
            body: JSON.stringify(Object.fromEntries(formData)),
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            localStorage.setItem("userEmail", email); // ✅ Save user email
            userFormContainer.style.display = 'none';
            document.body.style.overflow = 'auto';

            // Fetch recommendations for returning user
            fetchRecommendations(email);


            // // Fetch recommendations for returning user
            // fetchRecommendations(email);
        })
        .catch(error => alert(error.message));
    });

    // Fetch and display most bought products
    fetchMostBoughtProducts();
});

// Fetch most bought products
function fetchMostBoughtProducts() {
    fetch('/most_bought')
        .then(response => response.json())
        .then(data => {
            displayMostBoughtProducts(data.most_bought_products);
        })
        .catch(error => console.error("Error fetching most bought products:", error));
}

// Display most bought products
function displayMostBoughtProducts(products) {
    const mostBoughtContainer = document.getElementById("most-bought-products");
    mostBoughtContainer.innerHTML = ''; // Clear previous content

    products.forEach(product => {
        const productElement = document.createElement("div");
        productElement.classList.add("product");
        productElement.innerHTML = `
            <img src="${product.image_url}" alt="${product.name}">
            <h3>${product.name}</h3>
            <p>Price: &#8377;${product.price}</p>
            <p>Purchased: ${product.purchase_count} times</p>
            <button class="buy-btn" data-product-id="${product.id}">Add to Cart</button> 
        `;
        mostBoughtContainer.appendChild(productElement);
    });
}

// Fetch recommendations based on user email
function fetchRecommendations(email) {
    fetch(`/recommendations/${email}`)
        .then(response => response.json())
        .then(data => {
            if (data.recommended_products) {
                displayRecommendedProducts(data.recommended_products);
            } else {
                alert("No recommendations found.");
            }
        })
        .catch(error => console.error("Error fetching recommendations:", error));
}

// Display recommended products
function displayRecommendedProducts(products) {
    const recommendedContainer = document.getElementById("recommended-products");

    const productElements = recommendedContainer.querySelectorAll('.product');
    productElements.forEach(element => element.remove());
    // recommendedContainer.innerHTML = ''; // Clear previous content

    products.forEach(product => {
        const productElement = document.createElement("div");
        productElement.classList.add("product");
        productElement.innerHTML = `
            <img src="${product.image_url}" alt="${product.name}">
            <h3>${product.name}</h3>
            <p>Price: &#8377;${product.price}</p>
            <button class="buy-btn" data-product-id="${product.id}">Add to Cart</button>
        `;
        recommendedContainer.appendChild(productElement);
    });
}

// ✅ Extract product details and send to backend
document.addEventListener("DOMContentLoaded", function () {
    let products = [];

    document.querySelectorAll(".showcase").forEach(product => {
        let name = product.querySelector(".showcase-title")?.innerText.trim();
        let category = product.querySelector(".showcase-category")?.innerText.trim();
        let priceText = product.querySelector(".price")?.innerText.trim();
        let imageUrl = product.querySelector(".showcase-img")?.getAttribute("src");
        let productId = product.querySelector(".buy-btn")?.getAttribute("data-product-id");

        let price = parseFloat(priceText.replace(/[^0-9.-]+/g, ""));

        products.push({
            id: productId,
            name: name,
            category: category,
            price: price,
            image_url: imageUrl
        });
    });

    if (products.length > 0) {
        fetch("http://127.0.0.1:5000/save_products", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(products)
        })
        .then(response => response.json())
        .then(data => console.log("Products saved:", data))
        .catch(error => console.error("Error:", error));
    }
});

// ✅ Cart System

// Attach event listeners for buy buttons using event delegation
document.addEventListener("click", function (event) {
    if (event.target.classList.contains("buy-btn")) {
        handleBuyButtonClick(event.target);
    }
});

// Handle Buy Button Click
function handleBuyButtonClick(button) {
    let productId = button.getAttribute("data-product-id");
    let productName = button.parentElement.querySelector("h3")? button.parentElement.querySelector("h3").innerText.trim(): "Product";
    let priceText = button.parentElement.querySelector("p")? button.parentElement.querySelector(".price").innerText.trim() : "0";
    let price = parseFloat(priceText.replace(/[^0-9.-]+/g, ""));

    let userEmail = localStorage.getItem("userEmail");
    if (!userEmail) {
        alert("Please log in before purchasing!");
        return;
    }

    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let existingProduct = cart.find(item => item.product_id === productId);
    if (existingProduct) {
        existingProduct.quantity += 1; // Increment quantity
        existingProduct.total_price += price; // Update total price
    } else {
        cart.push({
            product_id: productId,
            product_name: productName,
            quantity: 1,
            total_price: price
        });
    }

    localStorage.setItem("cart", JSON.stringify(cart));
    alert(`${productName} has been added to your cart!`);
}

// ✅ Checkout Functionality
document.getElementById("checkout-btn").addEventListener("click", function () {
    let userEmail = localStorage.getItem("userEmail");
    if (!userEmail) {
        alert("Please log in before checking out!");
        return;
    }

    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    if (cart.length === 0) {
        alert("Your cart is empty!");
        return;
    }

    let transactionData = {
        user_email: userEmail,
        items: cart
    };

    fetch("http://127.0.0.1:5000/save_transaction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(transactionData)
    })
    .then(response => response.json())
    .then(data => {
        alert("Transaction successful!");
        localStorage.removeItem("cart");
        cart = [];
    })
    .catch(error => {
        console.error("Transaction error:", error);
        alert("Transaction failed.");
    });
});

// Search functionality
function performSearch() {
    const query = document.getElementById('search-input').value;
    fetch(`/search?query=${query}`)
        .then(response => response.json())
        .then(data => {
            if (data.products && data.products.length > 0) {
                displaySearchResults(data.products);
            } else {
                alert("No products found.");
            }
        })
        .catch(error => console.error('Error:', error));
}

// Display search results
function displaySearchResults(products) {
    const resultsContainer = document.getElementById("search-results"); // Make sure you have this container in your HTML
    resultsContainer.innerHTML = ''; // Clear previous results

    products.forEach(product => {
        const productElement = document.createElement("div");
        productElement.classList.add("product");
        productElement.innerHTML = `
            <img src="${product.image_url}" alt="${product.name}">
            <h3>${product.name}</h3>
            <p>Category: ${product.category}</p>
            <p>Price: &#8377;${product.price}</p>
            <button class="buy-btn" data-product-id="${product.id}">Add to Cart</button>
        `;
        resultsContainer.appendChild(productElement);
    });
}