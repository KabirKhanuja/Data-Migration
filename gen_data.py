import csv
from faker import Faker
from random import randint, choice, random
from tqdm import trange

fake = Faker()
N_CUSTOMERS = 200_000      
N_PRODUCTS = 50_000
N_ORDERS = 500_000
N_ORDER_ITEMS = 1_000_000 

# customers.csv
with open('customers.csv','w',newline='') as f:
    w = csv.writer(f)
    w.writerow(['customer_id','name','email','city','age'])
    for i in trange(N_CUSTOMERS):
        w.writerow([i+1, fake.name(), fake.email(), fake.city(), randint(18,80)])

# products.csv
with open('products.csv','w',newline='') as f:
    w = csv.writer(f)
    w.writerow(['product_id','name','price','category'])
    for i in trange(N_PRODUCTS):
        w.writerow([i+1, fake.word().title(), round(random()*500,2), choice(['A','B','C','D'])])

# orders.csv
with open('orders.csv','w',newline='') as f:
    w = csv.writer(f)
    w.writerow(['order_id','customer_id','order_date','total_amt'])
    for i in trange(N_ORDERS):
        cust = randint(1, N_CUSTOMERS)
        w.writerow([i+1, cust, fake.date_between(start_date='-2y', end_date='today').isoformat(), round(random()*2000,2)])

# order_items.csv
with open('order_items.csv','w',newline='') as f:
    w = csv.writer(f)
    w.writerow(['order_item_id','order_id','product_id','qty','price'])
    for i in trange(N_ORDER_ITEMS):
        order = randint(1, N_ORDERS)
        prod = randint(1, N_PRODUCTS)
        qty = randint(1,5)
        price = round(random()*500,2)
        w.writerow([i+1, order, prod, qty, price])