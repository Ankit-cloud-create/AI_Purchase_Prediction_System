const API_BASE = "http://127.0.0.1:5000";

let allProducts = [];


/* =========================
   LOAD PRODUCTS
========================= */

async function loadProducts() {

    const productGrid = document.getElementById("product-grid");
    const loading = document.getElementById("loading");
    const productCount = document.getElementById("product-count");

    try {

        const response = await fetch(
            `${API_BASE}/api/products`
        );

        if (!response.ok) {
            throw new Error("Failed to load products");
        }

        allProducts = await response.json();

        loading.classList.add("hidden");

        productCount.textContent =
            `${allProducts.length} products`;

        displayProducts(allProducts);

    } catch (error) {

        console.error(error);

        loading.textContent =
            "Unable to connect to the recommendation system.";

    }
}


/* =========================
   DISPLAY PRODUCTS
========================= */

function displayProducts(products) {

    const productGrid =
        document.getElementById("product-grid");

    const noProducts =
        document.getElementById("no-products");

    productGrid.innerHTML = "";

    if (products.length === 0) {

        noProducts.classList.remove("hidden");

        return;
    }

    noProducts.classList.add("hidden");

    products.forEach(product => {

        const card =
            document.createElement("div");

        card.className = "product-card";

        card.innerHTML = `
            <div class="product-image">
                <img
                    src="../images/${product.image}"
                    alt="${product.name}"
                    onerror="this.style.display='none'"
                >
            </div>

            <div class="product-info">

                <div class="product-name">
                    ${product.name}
                </div>

                <div class="product-brand">
                    ${product.brand}
                </div>

                <span class="product-category">
                    ${product.category}
                </span>

            </div>
        `;

        card.addEventListener(
            "click",
            () => selectProduct(product)
        );

        productGrid.appendChild(card);

    });
}


/* =========================
   SELECT PRODUCT
========================= */

async function selectProduct(product) {

    showSelectedProduct(product);

    await getRecommendations(product.name);

}


/* =========================
   SHOW SELECTED PRODUCT
========================= */

function showSelectedProduct(product) {

    const section =
        document.getElementById("selected-section");

    const container =
        document.getElementById("selected-product");

    section.classList.remove("hidden");

    container.innerHTML = `

        <div class="selected-card">

            <div class="product-image">

                <img
                    src="../images/${product.image}"
                    alt="${product.name}"
                    onerror="this.style.display='none'"
                >

            </div>

            <div>

                <div class="selected-label">
                    Selected Product
                </div>

                <h3>
                    ${product.name}
                </h3>

                <p>
                    ${product.brand}
                </p>

                <p>
                    ${product.category}
                </p>

            </div>

        </div>

    `;

    section.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


/* =========================
   GET RECOMMENDATIONS
========================= */

async function getRecommendations(productName) {

    const recommendationSection =
        document.getElementById(
            "recommendation-section"
        );

    const recommendationGrid =
        document.getElementById(
            "recommendation-grid"
        );

    recommendationSection.classList.remove(
        "hidden"
    );

    recommendationGrid.innerHTML = `
        <div class="loading">
            Finding associated products...
        </div>
    `;

    try {

        const response = await fetch(
            `${API_BASE}/api/recommend`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    product: productName
                })
            }
        );

        if (!response.ok) {
            throw new Error(
                "Recommendation request failed"
            );
        }

        const data =
            await response.json();

        displayRecommendations(
            data.recommendations
        );

    } catch (error) {

        console.error(error);

        recommendationGrid.innerHTML = `
            <div class="loading">
                Unable to load recommendations.
            </div>
        `;

    }
}


/* =========================
   DISPLAY RECOMMENDATIONS
========================= */

function displayRecommendations(
    recommendations
) {

    const recommendationGrid =
        document.getElementById(
            "recommendation-grid"
        );

    recommendationGrid.innerHTML = "";

    if (
        !recommendations ||
        recommendations.length === 0
    ) {

        recommendationGrid.innerHTML = `
            <div class="loading">
                No associated products were found
                for this selection.
            </div>
        `;

        return;
    }


    recommendations.forEach(
        recommendation => {

            const product =
                allProducts.find(
                    item =>
                        item.name ===
                        recommendation.product
                );

            if (!product) {
                return;
            }


            const card =
                document.createElement("div");

            card.className =
                "recommendation-card";


            const confidence =
                (
                    recommendation.confidence *
                    100
                ).toFixed(1);


            const lift =
                Number(
                    recommendation.lift
                ).toFixed(2);


            card.innerHTML = `

                <div class="product-image">

                    <img
                        src="../images/${product.image}"
                        alt="${product.name}"
                        onerror="this.style.display='none'"
                    >

                </div>


                <div class="recommendation-info">

                    <h3>
                        ${product.name}
                    </h3>

                    <div class="brand">
                        ${product.brand}
                    </div>


                    <span class="product-category">
                        ${product.category}
                    </span>


                    <div class="metrics">

                        <div class="metric">

                            <span>
                                Confidence
                            </span>

                            <strong>
                                ${confidence}%
                            </strong>

                        </div>


                        <div class="metric">

                            <span>
                                Lift
                            </span>

                            <strong>
                                ${lift}
                            </strong>

                        </div>

                    </div>

                </div>

            `;


            recommendationGrid.appendChild(
                card
            );

        }
    );


    document
        .getElementById(
            "recommendation-section"
        )
        .scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
}


/* =========================
   SEARCH
========================= */

document
    .getElementById("search-input")
    .addEventListener(
        "input",
        function () {

            const searchTerm =
                this.value
                    .toLowerCase()
                    .trim();


            const filteredProducts =
                allProducts.filter(
                    product =>
                        product.name
                            .toLowerCase()
                            .includes(searchTerm)
                        ||
                        product.brand
                            .toLowerCase()
                            .includes(searchTerm)
                        ||
                        product.category
                            .toLowerCase()
                            .includes(searchTerm)
                );


            document.getElementById(
                "product-count"
            ).textContent =
                `${filteredProducts.length} products`;


            displayProducts(
                filteredProducts
            );

        }
    );


/* =========================
   START APPLICATION
========================= */

loadProducts();