import pandas as pd
from ourapp.models import Store, Item, Inventory

def get_dataframes() -> tuple[pd.DataFrame, pd.DataFrame]:
    items_df = pd.read_csv('./input_data/items.csv', delimiter=';')
    items_df.columns = ['store_number', 'sku_number', 'product_group_number', 'stock', "minimum_required_stock", 'demand']

    stores_df = pd.read_csv('./input_data/stores.csv', delimiter=';')
    return items_df, stores_df

def create_stores_and_items(items_df):
    stores = {store_number: Store.objects.get_or_create(id=store_number)[0] for store_number in items_df['store_number'].unique()}
    items = {sku_number: Item.objects.get_or_create(id=sku_number)[0] for sku_number in items_df['sku_number'].unique()}
    return stores, items

def update_inventory(items_df, stores, items):
    for _, row in items_df.iterrows():
        store = stores[row['store_number']]
        item = items[row['sku_number']]
        Inventory.objects.update_or_create(
            store=store,
            item=item,
            defaults={
                'quantity': row['stock'],
                'demand': row['demand'],
                'minimum_required': row['minimum_required_stock']
            }
        )

def update_stores(stores_df, stores):
    for _, row in stores_df.iterrows():
        store_number = row['Store Number']
        if store_number in stores:
            store = stores[store_number]
            store.x_coordinate = float(row['X-Koordinates'].replace(',', '.'))
            store.y_coordinate = float(row['Y-Koordinates'].replace(',', '.'))
            store.federal_state = row["Federal State"]
            store.warehouse = row["Warehouse"]
            store.storage_area = float(row["Storage Area"].replace(',', '.'))
            store.save()

if Inventory.objects.exists():
    exit()
items_df, stores_df = get_dataframes()
stores, items = create_stores_and_items(items_df)
update_inventory(items_df, stores, items)
update_stores(stores_df, stores)
