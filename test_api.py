from app import app


client = app.test_client()


def test_cart(cart):
    response = client.post(
        "/api/recommend",
        json={"cart": cart}
    )

    print("\n" + "=" * 70)
    print("CART:", cart)
    print("STATUS:", response.status_code)
    print("RESPONSE:")
    print(response.get_json())


# ------------------------------------------------------------
# Test 1: Multi-item cart
# ------------------------------------------------------------

test_cart([
    "Cooking Oil",
    "Salt",
    "Toor Dal"
])


# ------------------------------------------------------------
# Test 2: Bread
# ------------------------------------------------------------

test_cart([
    "Bread"
])


# ------------------------------------------------------------
# Test 3: Rice
# ------------------------------------------------------------

test_cart([
    "Rice"
])


# ------------------------------------------------------------
# Test 4: Product with no qualifying single-item rule
# ------------------------------------------------------------

test_cart([
    "Toothpaste"
])


# ------------------------------------------------------------
# Test 5: Multi-item cart where an existing recommendation
# should not be recommended again
# ------------------------------------------------------------

test_cart([
    "Bread",
    "Milk"
])