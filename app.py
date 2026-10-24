from datetime import datetime
import io
from contextlib import redirect_stdout
import streamlit as st


# ==========================================
# CORE CLASSES (Preserved from your project)
# ==========================================
class ItemToPurchase:

    def __init__(self, item_name="none", item_price=0.0, item_quantity=0):
        self.item_name = item_name
        self.item_price = float(item_price)
        self.item_quantity = int(item_quantity)

    def print_item_cost(self):
        total_cost = self.item_price * self.item_quantity
        print(
            f"{self.item_name} {self.item_quantity} @ ${self.item_price:g} = ${total_cost:g}"
        )


class ShoppingCart:

    def __init__(self, customer_name="none", current_date="January 1, 2025"):
        self.customer_name = customer_name
        self.current_date = current_date
        self.cart_items = []

    def add_item(self, item_to_purchase):
        for item in self.cart_items:
            if item.item_name.lower() == item_to_purchase.item_name.lower():
                item.item_quantity += item_to_purchase.item_quantity
                return
        self.cart_items.append(item_to_purchase)

    def remove_item(self, item_name):
        for item in self.cart_items:
            if item.item_name.lower() == item_name.lower():
                self.cart_items.remove(item)
                return True
        print("Item not found in cart. Nothing removed.")
        return False

    def modify_item(self, item_to_purchase):
        for item in self.cart_items:
            if item.item_name.lower() == item_to_purchase.item_name.lower():
                if item_to_purchase.item_quantity != 0:
                    item.item_quantity = item_to_purchase.item_quantity
                return True
        print("Item not found in cart. Nothing modified.")
        return False

    def get_num_items_in_cart(self):
        return sum(item.item_quantity for item in self.cart_items)

    def get_cost_of_cart(self):
        return sum(
            item.item_price * item.item_quantity for item in self.cart_items
        )

    def print_total(self):
        print(f"{self.customer_name}'s Shopping Cart - {self.current_date}")

        if len(self.cart_items) == 0:
            print("SHOPPING CART IS EMPTY")
            return

        for item in self.cart_items:
            item.print_item_cost()
        num_items = self.get_num_items_in_cart()
        print(f"Number of Items: {num_items}\n")
        total_cost = self.get_cost_of_cart()
        print(f"Total: ${total_cost:g}")


# ==========================================
# STREAMLIT GUI APPLICATION
# ==========================================
st.set_page_config(
    page_title="Online Shopping Cart",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for polished cards and layout
st.markdown(
    """
    <style>
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    @media (prefers-color-scheme: dark) {
        div[data-testid="metric-container"] {
            background-color: #1e2127;
            border: 1px solid #2e333d;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize ShoppingCart in Streamlit Session State
if "cart" not in st.session_state:
    default_date = datetime.now().strftime("%B %d, %Y")
    st.session_state.cart = ShoppingCart("Mandeep Singh", default_date)

cart: ShoppingCart = st.session_state.cart

# --- SIDEBAR: CUSTOMER DETAILS & QUICK PRESETS ---
with st.sidebar:
    st.header("👤 Customer Details")
    new_name = st.text_input("Customer Name", value=cart.customer_name)
    new_date = st.text_input("Today's Date", value=cart.current_date)

    # Sync changes immediately
    cart.customer_name = new_name.strip() if new_name.strip() else "none"
    cart.current_date = (
        new_date.strip() if new_date.strip() else "January 1, 2025"
    )

    st.divider()
    st.subheader("⚡ Quick Demo Actions")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("Load Sample Items", use_container_width=True):
            cart.add_item(ItemToPurchase("Nike Romaleos", 189, 2))
            cart.add_item(ItemToPurchase("Chocolate Chips", 3, 5))
            cart.add_item(ItemToPurchase("Powerbeats 2 Headphones", 128, 1))
            st.toast("Sample items added to cart!", icon="✅")
            st.rerun()
    with col_s2:
        if st.button("Clear Cart", type="secondary", use_container_width=True):
            cart.cart_items.clear()
            st.toast("Cart cleared!", icon="🗑️")
            st.rerun()

# --- MAIN PAGE HEADER & METRICS ---
st.title(f"🛒 {cart.customer_name}'s Shopping Cart")
st.caption(f"📅 **Date:** {cart.current_date}")

m1, m2, m3 = st.columns(3)
m1.metric("Total Items in Cart", f"{cart.get_num_items_in_cart()}")
m2.metric("Unique Products", f"{len(cart.cart_items)}")
m3.metric("Total Cart Cost", f"${cart.get_cost_of_cart():,.2f}")

st.divider()

# --- TWO-COLUMN WORKSPACE ---
left_col, right_col = st.columns([1, 1.4], gap="large")

# LEFT COLUMN: Menu Actions (Add, Modify, Remove)
with left_col:
    st.subheader("⚙️ Cart Actions (Menu)")
    tab_add, tab_mod, tab_rem = st.tabs(
        ["➕ Add Item (a)", "✏️ Change Qty (c)", "🗑️ Remove Item (r)"]
    )

    # Tab 1: Add Item
    with tab_add:
        with st.form("add_item_form", clear_on_submit=True):
            st.markdown("##### Add a New Item to Cart")
            item_name = st.text_input(
                "Item Name", placeholder="e.g., Bottled Water"
            )
            c1, c2 = st.columns(2)
            with c1:
                item_price = st.number_input(
                    "Item Price ($)", min_value=0.0, step=0.5, format="%.2f"
                )
            with c2:
                item_qty = st.number_input(
                    "Quantity", min_value=1, value=1, step=1
                )

            submitted_add = st.form_submit_button(
                "Add to Cart", type="primary", use_container_width=True
            )
            if submitted_add:
                if not item_name.strip():
                    st.error("Please enter an item name.")
                else:
                    cart.add_item(
                        ItemToPurchase(item_name.strip(), item_price, item_qty)
                    )
                    st.toast(
                        f"Added {item_qty}x '{item_name.strip()}' to cart!",
                        icon="🛍️",
                    )
                    st.rerun()

    # Tab 2: Modify Item Quantity
    with tab_mod:
        if not cart.cart_items:
            st.info("Your cart is empty. Add items first to modify quantities.")
        else:
            item_names = [item.item_name for item in cart.cart_items]
            selected_mod_item = st.selectbox(
                "Select Item to Modify", options=item_names
            )

            # Find current quantity for default display
            current_qty = next(
                (
                    i.item_quantity
                    for i in cart.cart_items
                    if i.item_name == selected_mod_item
                ),
                1,
            )
            new_qty = st.number_input(
                "Enter New Quantity", min_value=1, value=current_qty, step=1
            )

            if st.button(
                "Update Quantity", type="primary", use_container_width=True
            ):
                mod_obj = ItemToPurchase(
                    item_name=selected_mod_item, item_quantity=new_qty
                )
                if cart.modify_item(mod_obj):
                    st.toast(
                        f"Updated '{selected_mod_item}' quantity to {new_qty}!",
                        icon="✏️",
                    )
                    st.rerun()

    # Tab 3: Remove Item
    with tab_rem:
        if not cart.cart_items:
            st.info("Your cart is empty. Nothing to remove.")
        else:
            item_names_rem = [item.item_name for item in cart.cart_items]
            selected_rem_item = st.selectbox(
                "Select Item to Remove", options=item_names_rem
            )

            if st.button(
                "Remove from Cart", type="primary", use_container_width=True
            ):
                if cart.remove_item(selected_rem_item):
                    st.toast(
                        f"Removed '{selected_rem_item}' from cart.", icon="🗑️"
                    )
                    st.rerun()

# RIGHT COLUMN: Live Cart View & Receipt Output
with right_col:
    st.subheader("🛍️ Current Cart Contents")

    if not cart.cart_items:
        st.warning("SHOPPING CART IS EMPTY")
    else:
        # Table Header
        h1, h2, h3, h4, h5 = st.columns([3, 1.5, 1.5, 1.5, 2.2])
        h1.markdown("**Item**")
        h2.markdown("**Price**")
        h3.markdown("**Qty**")
        h4.markdown("**Subtotal**")
        h5.markdown("**Quick Edit**")
        st.divider()

        # Render each item row with interactive +/-/Delete buttons
        for idx, item in enumerate(list(cart.cart_items)):
            c1, c2, c3, c4, c5 = st.columns([3, 1.5, 1.5, 1.5, 2.2])
            subtotal = item.item_price * item.item_quantity

            c1.write(f"**{item.item_name}**")
            c2.write(f"${item.item_price:g}")
            c3.write(f"`{item.item_quantity}`")
            c4.write(f"**${subtotal:g}**")

            b_minus, b_plus, b_del = c5.columns(3)
            with b_minus:
                if st.button("➖", key=f"dec_{idx}", help="Decrease quantity"):
                    if item.item_quantity > 1:
                        cart.modify_item(
                            ItemToPurchase(
                                item.item_name,
                                item_quantity=item.item_quantity - 1,
                            )
                        )
                    else:
                        cart.remove_item(item.item_name)
                    st.rerun()
            with b_plus:
                if st.button("➕", key=f"inc_{idx}", help="Increase quantity"):
                    cart.modify_item(
                        ItemToPurchase(
                            item.item_name, item_quantity=item.item_quantity + 1
                        )
                    )
                    st.rerun()
            with b_del:
                if st.button("🗑️", key=f"del_{idx}", help="Remove item"):
                    cart.remove_item(item.item_name)
                    st.rerun()

        st.divider()
        _, total_col = st.columns([2, 1])
        with total_col:
            st.markdown(f"### Total: `${cart.get_cost_of_cart():g}`")

    # Classic Console Receipt Output (Calls your original print_total() method)
    with st.expander(
        "🧾 View Classic Console Receipt (`o - Output shopping cart`)",
        expanded=True,
    ):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            cart.print_total()
        receipt_text = buffer.getvalue()
        st.code(receipt_text, language="text")
