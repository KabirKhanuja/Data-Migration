CREATE TABLE customers (
  customer_id SERIAL PRIMARY KEY,
  name TEXT,
  email TEXT,
  city TEXT,
  age INT
);

CREATE TABLE products (
  product_id SERIAL PRIMARY KEY,
  name TEXT,
  price NUMERIC,
  category TEXT
);

CREATE TABLE orders (
  order_id SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(customer_id),
  order_date DATE,
  total_amt NUMERIC
);

CREATE TABLE order_items (
  order_item_id SERIAL PRIMARY KEY,
  order_id INT REFERENCES orders(order_id),
  product_id INT REFERENCES products(product_id),
  qty INT,
  price NUMERIC
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orderitems_order ON order_items(order_id);
CREATE INDEX idx_orderitems_product ON order_items(product_id);