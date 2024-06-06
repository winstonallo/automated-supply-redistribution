from ourapp.models import Item, Store, Inventory, Order, OrderItem
from collections import deque
from bisect import insort_right
from copy import deepcopy
from oursolution.settings import TYPE_MINIMAL, TYPE_SIMPLE

class Calculation:
    
    def __init__(self):
        self.allstokes_minimal_demand = {}
        self.allstokes_simple_demand = {}
        self.previous_state_minimal = {}
        self.previous_state_simple = {}
        self.operations = {}
        self.count = 0
        
    def print_statistics(self, type):
        if type == TYPE_MINIMAL:
            cur_stokes = self.allstokes_minimal_demand
            previous_state = self.previous_state_minimal
        elif type == TYPE_SIMPLE:
            cur_stokes = self.allstokes_simple_demand
            previous_state = self.previous_state_simple
        sum_after = 0
        sum_overstoke_after = 0
        count_overstoke_after = 0
        sum_understock_after = 0
        count_understock_after = 0
        with open(f"output{self.count}.txt", "a") as f:
            self.count += 1
            f.write("Store;Item;Quantity\n")
            for item_id in cur_stokes:
                for store_id in cur_stokes[item_id]:
                    temp = cur_stokes[item_id][store_id]
                    sum_after += abs(cur_stokes[item_id][store_id])
                    if temp > 0:
                        sum_overstoke_after += temp
                        count_overstoke_after += 1
                    elif temp < 0:
                        sum_understock_after += abs(temp)
                        count_understock_after += 1
                    # f.write(f"{store_id};{item_id};{cur_stokes[item_id][store_id]}\n")
            sum_before = 0
            sum_overstoke_before = 0
            count_overstoke_before = 0
            sum_understock_before = 0
            count_understock_before = 0
            for item_id in previous_state:
                for store_id in previous_state[item_id]:
                    temp = previous_state[item_id][store_id]
                    sum_before += abs(previous_state[item_id][store_id])
                    if temp > 0:
                        sum_overstoke_before += temp
                        count_overstoke_before += 1
                    elif temp < 0:
                        sum_understock_before += abs(temp)
                        count_understock_before += 1

            f.write(f"\nSum before: {sum_before}\n")
            f.write(f"Sum after: {sum_after}\n\n")

            f.write(f"Sum overstoke before: {sum_overstoke_before}\n")
            f.write(f"Sum overstoke after: {sum_overstoke_after}\n\n")
            
            f.write(f"Count overstoke before: {count_overstoke_before}\n")
            f.write(f"Count overstoke after: {count_overstoke_after}\n\n")

            f.write(f"Sum understock before: {sum_understock_before}\n")
            f.write(f"Sum understock after: {sum_understock_after}\n\n")

            f.write(f"Count understock after: {count_understock_after}\n")
            f.write(f"Count understock before: {count_understock_before}\n\n")        

    def get_all_data_from_stores(self):
        all_items = Item.objects.all()
        for item in all_items:
            self.allstokes_minimal_demand[item.id] = {}
            self.allstokes_simple_demand[item.id] = {}
            inventories = Inventory.objects.filter(item=item)
            for inventory in inventories:
                self.allstokes_minimal_demand[item.id][inventory.store.id] = inventory.quantity - inventory.minimum_required
                self.allstokes_simple_demand[item.id][inventory.store.id] = inventory.quantity - inventory.demand
        self.previous_state_simple = deepcopy(self.allstokes_simple_demand)
        self.previous_state_minimal = deepcopy(self.allstokes_minimal_demand)

    def get_best_option_from_history(self, store_sender_id, item_id, type):
        if type == TYPE_MINIMAL:
            cur_stokes = self.allstokes_minimal_demand
        elif type == TYPE_SIMPLE:
            cur_stokes = self.allstokes_simple_demand
        best_option_value = None
        best_option_store_receiver_id = None
        if store_sender_id not in self.operations:
            return None 
        for store_receiver_id in self.operations[store_sender_id]:
            if store_receiver_id not in cur_stokes[item_id]:
                continue
            store_needs = cur_stokes[item_id][store_receiver_id]
            if store_needs >= 0:
                continue
            sent_before = sum(self.operations[store_sender_id][store_receiver_id].values())
            if best_option_value is None or sent_before < best_option_value:
                best_option_value = sent_before + store_needs
                best_option_store_receiver_id = store_receiver_id
        return best_option_store_receiver_id
    
    def apply_operations(self):
        for store_sender_id in self.operations:
            for store_receiver_id in self.operations[store_sender_id]:
                for item_id in self.operations[store_sender_id][store_receiver_id]:
                    self.allstokes_simple_demand[item_id][store_sender_id] -= self.operations[store_sender_id][store_receiver_id][item_id]
                    self.allstokes_simple_demand[item_id][store_receiver_id] += self.operations[store_sender_id][store_receiver_id][item_id]
    
    def save_operations_to_db(self):
        Order.objects.all().delete()
        OrderItem.objects.all().delete()
        for sender_id in self.operations:
            for receiver_id in self.operations[sender_id]:
                order = Order.objects.create(source_store_id=sender_id, destination_store_id=receiver_id)
                for item_id in self.operations[sender_id][receiver_id]:
                    OrderItem.objects.create(order=order, item_id=item_id, quantity=self.operations[sender_id][receiver_id][item_id])

    def print_operations(self):
        with open("operations.txt", "w") as f:
            f.write("From store;To store;Item;Quantity\n")
            for store_sender_id in self.operations:
                for store_receiver_id in self.operations[store_sender_id]:
                    for item_id in self.operations[store_sender_id][store_receiver_id]:
                        f.write(f"{store_sender_id};{store_receiver_id};{item_id};{self.operations[store_sender_id][store_receiver_id][item_id]}\n")

    def calculate_redistribution(self, type):
        if type == TYPE_MINIMAL:
            cur_stokes = self.allstokes_minimal_demand
        elif type == TYPE_SIMPLE:
            cur_stokes = self.allstokes_simple_demand
        for item_id in cur_stokes:
            while True:
                current_item_deque = deque(sorted(cur_stokes[item_id].items(), key=lambda x: x[1]))
                first, last = 0, len(current_item_deque) - 1
                store_sender_id, quantity_sender = current_item_deque[last]
                store_receiver_id, quantity_receiver = current_item_deque[first]
                if quantity_sender >= 0 and quantity_receiver >= 0:
                    break
                elif quantity_sender == 0:
                    break
                elif quantity_sender < 0 and quantity_receiver < 0:
                    break

                items_to_send = abs(min(quantity_sender, quantity_receiver))
                best_option_from_history_id = self.get_best_option_from_history(store_sender_id, item_id, type)
                if best_option_from_history_id is not None:
                    history_value = sum(self.operations[store_sender_id][best_option_from_history_id].values()) + abs(cur_stokes[item_id][best_option_from_history_id])
                    if items_to_send < history_value:
                        store_receiver_id = best_option_from_history_id
                        items_to_send = min(quantity_sender, abs(cur_stokes[item_id][best_option_from_history_id]))

                if store_sender_id not in self.operations:
                    self.operations[store_sender_id] = {}
                if store_receiver_id not in self.operations[store_sender_id]:
                    self.operations[store_sender_id][store_receiver_id] = {}
                if item_id not in self.operations[store_sender_id][store_receiver_id]:
                    self.operations[store_sender_id][store_receiver_id][item_id] = 0

                self.operations[store_sender_id][store_receiver_id][item_id] += items_to_send
                cur_stokes[item_id][store_sender_id] -= items_to_send
                cur_stokes[item_id][store_receiver_id] += items_to_send
                current_item_deque[last] = store_sender_id, cur_stokes[item_id][store_sender_id]
                current_item_deque[first] = store_receiver_id, cur_stokes[item_id][store_receiver_id]
                
                if cur_stokes[item_id][store_sender_id] == 0:
                    current_item_deque.pop()
                else:
                    current_item_deque[last] = (store_sender_id, cur_stokes[item_id][store_sender_id])
                if cur_stokes[item_id][store_receiver_id] == 0:
                    current_item_deque.popleft()
                else:
                    current_item_deque[first] = (store_receiver_id, cur_stokes[item_id][store_receiver_id])
        return self.operations

if not OrderItem.objects.exists():
    calculation = Calculation()
    calculation.get_all_data_from_stores()
    print("Got data from stores")
    calculation.calculate_redistribution(TYPE_MINIMAL)
    print("Calculated redistribution")
    calculation.print_statistics(TYPE_MINIMAL)
    print("Printed statistics")
    calculation.apply_operations()
    print("Applied operations")
    calculation.calculate_redistribution(TYPE_SIMPLE)
    print("Calculated redistribution")
    calculation.print_statistics(TYPE_SIMPLE)
    print("Printed statistics")
    calculation.save_operations_to_db()
