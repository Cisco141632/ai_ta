import os.path
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# Set random seed for reproducible data
random.seed(42)
np.random.seed(42)


class DataGen:
    def __init__(self):
        self.user_table_name = "users"
        self.category_table_name = "categories"
        self.product_table_name = "products"
        self.order_table_name = "orders"
        self.order_items_table_name = "order_items"
        self.review_table_name = "reviews"

    @staticmethod
    def generate_users_csv(num_users=1000):
        """Generate users data"""
        users_data = []

        first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emma', 'Chris', 'Lisa', 'Tom', 'Anna',
                       'James', 'Mary', 'Robert', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                      'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson']

        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
                  'San Antonio', 'San Diego', 'Dallas', 'San Jose']

        tiers = ['Bronze', 'Silver', 'Gold', 'Platinum']

        for i in range(num_users):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)

            user = {
                'user_id': i + 1,
                'email': f"{first_name.lower()}.{last_name.lower()}{i + 1}@email.com",
                'first_name': first_name,
                'last_name': last_name,
                # FIX: Use datetime object instead of string
                'registration_date': datetime.now() - timedelta(days=random.randint(1, 730)),
                'city': random.choice(cities),
                'customer_tier': np.random.choice(tiers, p=[0.5, 0.3, 0.15, 0.05]),
                'is_active': random.choice([True, False])
            }
            users_data.append(user)

        df = pd.DataFrame(users_data)
        # Ensure registration_date is datetime type
        df['registration_date'] = pd.to_datetime(df['registration_date'])
        return df

    @staticmethod
    def generate_categories_csv():
        """Generate product categories"""
        categories = [
            {'category_id': 1, 'category_name': 'Electronics', 'parent_category_id': None},
            {'category_id': 2, 'category_name': 'Clothing', 'parent_category_id': None},
            {'category_id': 3, 'category_name': 'Home & Garden', 'parent_category_id': None},
            {'category_id': 4, 'category_name': 'Sports', 'parent_category_id': None},
            {'category_id': 5, 'category_name': 'Books', 'parent_category_id': None},

            # Subcategories
            {'category_id': 6, 'category_name': 'Smartphones', 'parent_category_id': 1},
            {'category_id': 7, 'category_name': 'Laptops', 'parent_category_id': 1},
            {'category_id': 8, 'category_name': 'Headphones', 'parent_category_id': 1},

            {'category_id': 9, 'category_name': 'Men Clothing', 'parent_category_id': 2},
            {'category_id': 10, 'category_name': 'Women Clothing', 'parent_category_id': 2},
            {'category_id': 11, 'category_name': 'Shoes', 'parent_category_id': 2},

            {'category_id': 12, 'category_name': 'Furniture', 'parent_category_id': 3},
            {'category_id': 13, 'category_name': 'Kitchen', 'parent_category_id': 3},

            {'category_id': 14, 'category_name': 'Fitness', 'parent_category_id': 4},
            {'category_id': 15, 'category_name': 'Outdoor', 'parent_category_id': 4},
        ]

        return pd.DataFrame(categories)

    @staticmethod
    def generate_products_csv(num_products=500):
        """Generate products data"""
        products_data = []

        # Product name templates by category
        product_names = {
            6: ['iPhone Pro', 'Samsung Galaxy', 'Google Pixel', 'OnePlus Phone'],  # Smartphones
            7: ['MacBook Pro', 'Dell XPS', 'HP Pavilion', 'Lenovo ThinkPad'],  # Laptops
            8: ['AirPods Pro', 'Sony WH-1000', 'Bose QuietComfort', 'Beats Studio'],  # Headphones
            9: ['Men T-Shirt', 'Men Jeans', 'Men Jacket', 'Men Polo'],  # Men Clothing
            10: ['Women Dress', 'Women Blouse', 'Women Skirt', 'Women Jeans'],  # Women Clothing
            11: ['Running Shoes', 'Casual Sneakers', 'Dress Shoes', 'Boots'],  # Shoes
            12: ['Office Chair', 'Dining Table', 'Sofa', 'Bookshelf'],  # Furniture
            13: ['Coffee Maker', 'Blender', 'Microwave', 'Toaster'],  # Kitchen
            14: ['Treadmill', 'Dumbbells', 'Yoga Mat', 'Exercise Bike'],  # Fitness
            15: ['Tent', 'Sleeping Bag', 'Backpack', 'Camping Chair']  # Outdoor
        }

        brands = ['Apple', 'Samsung', 'Sony', 'Nike', 'Adidas', 'HP', 'Dell', 'LG', 'Canon', 'Bosch']

        category_ids = list(range(6, 16))  # Subcategories only

        for i in range(num_products):
            category_id = random.choice(category_ids)
            base_names = product_names.get(category_id, ['Generic Product'])

            product = {
                'product_id': i + 1,
                'product_name': f"{random.choice(brands)} {random.choice(base_names)} {random.choice(['Pro', 'Elite', 'Standard'])}",
                'category_id': category_id,
                'price': round(random.uniform(10, 2000), 2),
                'cost_price': round(random.uniform(5, 1000), 2),
                # FIX: Use datetime object instead of string
                'launch_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'is_active': random.choice([True, False]),
                'average_rating': round(random.uniform(1, 5), 2),
                'total_reviews': random.randint(0, 1000)
            }
            products_data.append(product)

        df = pd.DataFrame(products_data)
        # Ensure launch_date is datetime type
        df['launch_date'] = pd.to_datetime(df['launch_date'])
        return df

    @staticmethod
    def generate_orders_csv(num_orders=2000, users_df=None, products_df=None):
        """Generate orders data"""
        if users_df is None or products_df is None:
            raise ValueError("Need users and products dataframes")

        orders_data = []
        statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
        status_weights = [0.05, 0.10, 0.15, 0.65, 0.05]

        payment_methods = ['credit_card', 'paypal', 'apple_pay', 'google_pay']

        for i in range(num_orders):
            user_id = random.choice(users_df['user_id'].tolist())
            order_date = datetime.now() - timedelta(days=random.randint(1, 365))
            status = np.random.choice(statuses, p=status_weights)

            # Calculate delivery date based on status
            delivered_date = None
            if status == 'delivered':
                delivered_date = order_date + timedelta(days=random.randint(1, 14))

            subtotal = round(random.uniform(20, 500), 2)
            tax_amount = round(subtotal * 0.08, 2)  # 8% tax
            shipping_cost = random.choice([0, 5.99, 9.99, 15.99])
            # FIX: Add missing discount_amount column
            discount_amount = round(random.uniform(0, 50), 2)
            total_amount = subtotal + tax_amount + shipping_cost - discount_amount

            order = {
                'order_id': i + 1,
                'user_id': user_id,
                # FIX: Use datetime object instead of string
                'order_date': order_date,
                'order_status': status,
                'subtotal': subtotal,
                'tax_amount': tax_amount,
                'shipping_cost': shipping_cost,
                'discount_amount': discount_amount,  # FIX: Added this column
                'total_amount': round(total_amount, 2),
                'payment_method': random.choice(payment_methods),
                'delivered_date': delivered_date  # FIX: Already datetime object
            }
            orders_data.append(order)

        df = pd.DataFrame(orders_data)
        # Ensure date columns are datetime type
        df['order_date'] = pd.to_datetime(df['order_date'])
        df['delivered_date'] = pd.to_datetime(df['delivered_date'])
        return df

    @staticmethod
    def generate_order_items_csv(orders_df=None, products_df=None):
        """Generate order items data"""
        if orders_df is None or products_df is None:
            raise ValueError("Need orders and products dataframes")

        order_items_data = []
        item_id = 1

        for _, order in orders_df.iterrows():
            # Each order has 1-5 items
            num_items = random.randint(1, 5)
            selected_products = random.sample(products_df['product_id'].tolist(),
                                              min(num_items, len(products_df)))

            for product_id in selected_products:
                product_price = products_df[products_df['product_id'] == product_id]['price'].iloc[0]
                quantity = random.randint(1, 3)

                item = {
                    'order_item_id': item_id,
                    'order_id': order['order_id'],
                    'product_id': product_id,
                    'quantity': quantity,
                    'unit_price': product_price,
                    'total_price': round(product_price * quantity, 2)
                }
                order_items_data.append(item)
                item_id += 1

        return pd.DataFrame(order_items_data)

    @staticmethod
    def generate_reviews_csv(num_reviews=800, orders_df=None, order_items_df=None, users_df=None):
        """Generate product reviews"""
        if any(df is None for df in [orders_df, order_items_df, users_df]):
            raise ValueError("Need orders, order_items, and users dataframes")

        # Only delivered orders can have reviews
        delivered_orders = orders_df[orders_df['order_status'] == 'delivered']

        reviews_data = []

        for i in range(min(num_reviews, len(delivered_orders))):
            order = delivered_orders.sample(1).iloc[0]
            order_items = order_items_df[order_items_df['order_id'] == order['order_id']]

            if len(order_items) > 0:
                item = order_items.sample(1).iloc[0]

                # Rating distribution (skewed positive)
                rating = np.random.choice([1, 2, 3, 4, 5], p=[0.05, 0.08, 0.15, 0.30, 0.42])

                # FIX: Use datetime object instead of string parsing
                order_date = order['order_date']
                if isinstance(order_date, str):
                    order_date = datetime.strptime(order_date, '%Y-%m-%d')
                review_date = order_date + timedelta(days=random.randint(1, 30))

                review = {
                    'review_id': i + 1,
                    'product_id': item['product_id'],
                    'user_id': order['user_id'],
                    'order_id': order['order_id'],
                    'rating': rating,
                    # FIX: Use datetime object instead of string
                    'review_date': review_date,
                    'helpful_votes': random.randint(0, 50)
                }
                reviews_data.append(review)

        df = pd.DataFrame(reviews_data)
        # Ensure review_date is datetime type
        df['review_date'] = pd.to_datetime(df['review_date'])
        return df

    def generate_all_csvs(self, folder: str):
        """Generate all CSV files"""
        print("Generating e-commerce CSV files...")

        # Generate data
        users_df = self.generate_users_csv(1000)
        categories_df = self.generate_categories_csv()
        products_df = self.generate_products_csv(500)
        orders_df = self.generate_orders_csv(2000, users_df, products_df)
        order_items_df = self.generate_order_items_csv(orders_df, products_df)
        reviews_df = self.generate_reviews_csv(800, orders_df, order_items_df, users_df)

        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        # Save to CSV files - convert datetime columns to strings for CSV
        users_df_csv = users_df.copy()
        users_df_csv['registration_date'] = users_df_csv['registration_date'].dt.strftime('%Y-%m-%d')

        products_df_csv = products_df.copy()
        products_df_csv['launch_date'] = products_df_csv['launch_date'].dt.strftime('%Y-%m-%d')

        orders_df_csv = orders_df.copy()
        orders_df_csv['order_date'] = orders_df_csv['order_date'].dt.strftime('%Y-%m-%d')
        orders_df_csv['delivered_date'] = orders_df_csv['delivered_date'].dt.strftime('%Y-%m-%d')
        orders_df_csv['delivered_date'] = orders_df_csv['delivered_date'].replace('NaT', '')

        reviews_df_csv = reviews_df.copy()
        reviews_df_csv['review_date'] = reviews_df_csv['review_date'].dt.strftime('%Y-%m-%d')

        users_df_csv.to_csv(f'{folder}/{self.user_table_name}.csv', index=False)
        categories_df.to_csv(f'{folder}/{self.category_table_name}.csv', index=False)
        products_df_csv.to_csv(f'{folder}/{self.product_table_name}.csv', index=False)
        orders_df_csv.to_csv(f'{folder}/{self.order_table_name}.csv', index=False)
        order_items_df.to_csv(f'{folder}/{self.order_items_table_name}.csv', index=False)
        reviews_df_csv.to_csv(f'{folder}/{self.review_table_name}.csv', index=False)

        print("\n📊 Data Summary:")
        print(f"Total Users: {len(users_df):,}")
        print(f"Total Products: {len(products_df):,}")
        print(f"Total Orders: {len(orders_df):,}")
        print(f"Total Order Items: {len(order_items_df):,}")
        print(f"Total Reviews: {len(reviews_df):,}")

    def generate_data(self):
        """Generate data and return DataFrames with proper datetime types"""
        users_df = self.generate_users_csv(1000)
        categories_df = self.generate_categories_csv()
        products_df = self.generate_products_csv(500)
        orders_df = self.generate_orders_csv(2000, users_df, products_df)
        order_items_df = self.generate_order_items_csv(orders_df, products_df)
        reviews_df = self.generate_reviews_csv(800, orders_df, order_items_df, users_df)

        # Print data types for debugging
        print("\n🔍 DataFrame Data Types:")
        print(f"Users registration_date: {users_df['registration_date'].dtype}")
        print(f"Products launch_date: {products_df['launch_date'].dtype}")
        print(f"Orders order_date: {orders_df['order_date'].dtype}")
        print(f"Orders delivered_date: {orders_df['delivered_date'].dtype}")
        print(f"Reviews review_date: {reviews_df['review_date'].dtype}")

        # Verify discount_amount column exists
        print(f"Orders columns: {list(orders_df.columns)}")

        return {
            self.user_table_name: users_df,
            self.category_table_name: categories_df,
            self.product_table_name: products_df,
            self.order_table_name: orders_df,
            self.order_items_table_name: order_items_df,
            self.review_table_name: reviews_df
        }