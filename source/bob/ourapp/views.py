from django.shortcuts import render
from django.db.models import Sum
from .models import Order, OrderItem, Store, Inventory
from .forms import StoreForm
import networkx as nx
import matplotlib.pyplot as plt
import os
from django.http import FileResponse
import matplotlib.colors as mcolors

import cartopy.crs as ccrs
import cartopy.feature as cfeature

def visualize_orders(orders_data, filename, input_store_id):
    G = nx.DiGraph()
    pos = {}
    x_coordinates = []
    y_coordinates = []

    all_store_ids = set(orders_data.keys()) | {input_store_id}
    for store_id in all_store_ids:
        try:
            store = Store.objects.get(id=store_id)
            if store.x_coordinate is not None and store.y_coordinate is not None:
                pos[store_id] = (store.x_coordinate, store.y_coordinate)
                x_coordinates.append(store.x_coordinate)
                y_coordinates.append(store.y_coordinate)
            else:
                print(f"Missing coordinate for store {store_id}.")
        except Store.DoesNotExist:
            print(f"Store with id {store_id} does not exist, not adding to map.")

    for order, items in orders_data.items():
        for item in items:
            destination_store_id = item.get("destination_store_id")
            if destination_store_id and destination_store_id in pos:
                if not G.has_edge(input_store_id, destination_store_id):
                    print(f"Adding edge from {input_store_id} to {destination_store_id} with weight {item.get('amount', 1)}")
                    G.add_edge(input_store_id, destination_store_id, weight=item.get("amount", 1))

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent([min(x_coordinates) - 1, max(x_coordinates) + 1, min(y_coordinates) - 1, max(y_coordinates) + 1], crs=ccrs.PlateCarree())

    for edge in G.edges():
        start_pos = pos[edge[0]]
        end_pos = pos[edge[1]]
        ax.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]], color="black", linewidth=1, marker='o', transform=ccrs.Geodetic())

    for store_id, (lon, lat) in pos.items():
        color = 'red' if store_id == input_store_id else 'blue'
        z_order = 5 if store_id == input_store_id else 3
        size = 100 if store_id == input_store_id else 50
        ax.scatter(lon, lat, color=color, s=size, transform=ccrs.PlateCarree(), zorder=z_order)
        ax.text(lon, lat, "", transform=ccrs.PlateCarree(), fontsize=8, ha='right', color=color)

    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')

    plt.savefig(filename)
    plt.close()






def get_orders_for_store(store_id: int, is_source: bool = False) -> dict:
    orders_data = {}
    orders_data[store_id] = []

    if is_source:
        orders = Order.objects.filter(source_store=store_id)
    else:
        orders = Order.objects.filter(destination_store=store_id)

    for order in orders:
        order_total = 0
        order_items = []
        for item in OrderItem.objects.filter(order=order):
            item_data = {
                "amount": item.quantity,
                "item_id": item.item.id,
            }
            order_items.append(item_data)
            order_total += item.quantity

        target_store_id = order.destination_store.id if is_source else order.source_store.id
        if target_store_id not in orders_data:
            orders_data[target_store_id] = []

        orders_data[target_store_id].append({
            "destination_store_id": target_store_id,
            "total_amount": order_total,
            "items": order_items
        })

    return orders_data



def orders_view(request):
    if request.method == "POST":
        form = StoreForm(request.POST)
        if form.is_valid():
            store_id = form.cleaned_data["store_id"]
            outgoing_orders = get_orders_for_store(store_id=store_id, is_source=True)
            incoming_orders = get_orders_for_store(store_id=store_id, is_source=False)

            visualize_orders(outgoing_orders, 'outgoing_orders.png', input_store_id=store_id)
            visualize_orders(incoming_orders, 'incoming_orders.png', input_store_id=store_id)

            outgoing_orders.pop(store_id)
            incoming_orders.pop(store_id)

            context = {
                "outgoing_orders": outgoing_orders,
                "incoming_orders": incoming_orders,
                "outgoing_orders_image": 'outgoing_orders.png',
                "incoming_orders_image": 'incoming_orders.png',
            }
            return render(request, "orders.html", context)
        else:
            return render(request, 'store_form.html', {'form': form})
    else:
        form = StoreForm()

    return render(request, 'store_form.html', {'form': form})


def stats_view(request):
    stores = Store.objects.order_by('id').annotate(
        total_stock=Sum('inventory__quantity'),
        total_mrs=Sum('inventory__minimum_required'),
        total_demand=Sum('inventory__demand')
    )
    store_ids = [store.id for store in stores]
    total_stocks = [store.total_stock for store in stores]
    total_mrs = [store.total_mrs for store in stores]
    total_demands = [store.total_demand for store in stores]
    context = {
        'inventory_data': {
            'store_id': store_ids,
            'store_stock': total_stocks,
            'store_mrs': total_mrs,
            'store_demand': total_demands,
        }
    }
    return render(request, "statistics.html", context)


def serve_image(request, filename):
    return FileResponse(open('images/' + filename, 'rb'))
