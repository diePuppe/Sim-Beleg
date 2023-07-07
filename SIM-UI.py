import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import simpy
import random
import threading

# Globale Variable für den aktuellen Simulations-Thread
current_simulation_thread = None

root = tk.Tk()  # Initialisieren des root-GUI-Fensters
summer = tk.BooleanVar(value=False)
semester_ferien = tk.BooleanVar(value=False)
selected_beer = tk.StringVar(value="Becks")


class Customer:
    def __init__(self, env, store, customer_type):
        self.env = env
        self.store = store
        self.customer_type = customer_type  # student oder normal

    def buy_beer(self):
        if self.customer_type == 'Student':
            if semester_ferien.get():
                if random.random() <= 0.25:  # Stellschraube: Wie viele Studenten kaufen während der Semesterferien ein
                    amount = random.randint(10, 20)  # Studenten kaufen während der Semesterferien mehr
                else:
                    return 0
            else:
                amount = random.randint(5, 10)  # Students kaufen 2-5 Bier während der Vorlesung  # Stellschraube
        else:
            amount = random.randint(1, 20)  # Normale Menschen kaufen 1-20 Bier

        beer_multiplier = 1.0
        if selected_beer.get() == "Landskron":
            beer_multiplier = 2.5  # Verkauf erhöht sich um 150%
        elif selected_beer.get() == "Hasseröder":
            beer_multiplier = 0.5  # Verkauf sinkt um 50%
        elif selected_beer.get() == "Feldschlößchen":
            beer_multiplier = 1.5  # Verkauf steigt um 50%
        elif selected_beer.get() == "Helles":
            beer_multiplier = 2.0  # Verkauf steigt um 100%

        if summer.get():
            beer_multiplier *= 2  # Im Sommer verdoppelt sich der Verkauf

        amount = int(amount * beer_multiplier)

        yield from self.store.buy_beer(amount)
        return amount


class BeerStore:
    def __init__(self, env, fig, canvas):
        self.env = env
        self.store = simpy.Container(env, init=10000, capacity=10000)  # ToDo: Nachfüllen des Bierbestandes
        self.total_beer_sold = 0
        self.student_beer_sales = [0] * 30
        self.daily_beer_sales = [0] * 30
        self.daily_customers = [0] * 30
        self.fig = fig
        self.canvas = canvas
        self.ax = self.fig.add_subplot(131)  # Bierverkauf Diagramm
        self.ax3 = self.fig.add_subplot(132)  # Kunden Diagramm
        self.ax2 = self.fig.add_subplot(133)  # Verkauf an Studenten Diagramm

    def buy_beer(self, amount):
        self.total_beer_sold += amount
        yield self.store.get(amount)
        self.daily_beer_sales[int(self.env.now) % 30] += amount
        self.update_graph()

    def student_buy_beer(self, amount):
        self.student_beer_sales[int(self.env.now) % 30] += amount

    def update_graph(self):
        self.ax.clear()
        self.ax.bar(range(len(self.daily_beer_sales)), self.daily_beer_sales, align='center', alpha=0.5)
        self.ax.set_xlabel('Tag im Monat')
        self.ax.set_ylabel('Verkaufte Bierflaschen')

        self.ax2.clear()
        self.ax2.bar(range(len(self.daily_customers)), self.daily_customers, align='center', alpha=0.5)
        self.ax2.set_xlabel('Tag im Monat')
        self.ax2.set_ylabel('Anzahl der Kunden')

        self.ax3.clear()
        self.ax3.bar(range(len(self.student_beer_sales)), self.student_beer_sales, align='center', alpha=0.5)
        self.ax3.set_xlabel('Tag im Monat')
        self.ax3.set_ylabel('Verkaufte Bierflaschen (Studenten)')

        self.canvas.draw()

    def add_customer(self, customer_type):
        self.daily_customers[int(self.env.now) % 30] += 1
        return Customer(self.env, self, customer_type)

    def run_simulation(self):
        for _ in range(31):
            num_customers = random.randint(10, 20)  # Anzahl der Kunden
            for _ in range(num_customers):
                customer_type = random.choice(['Regular', 'Student'])  # Hier könnte man noch angeben, in welchem Verhältnis Studenten und Kunden kommen
                customer = self.add_customer(customer_type)
                amount = yield from customer.buy_beer()
                if customer_type == 'Student' and amount > 0:  # Nur wenn der Student tatsächlich Bier kauft
                    self.student_buy_beer(amount)
            yield self.env.timeout(1)  # Ein Tag vergeht


def simulation_thread(fig, canvas):
    env = simpy.Environment()
    store = BeerStore(env, fig, canvas)
    env.process(store.run_simulation())
    env.run()


def main(fig, canvas):
    global current_simulation_thread

    if current_simulation_thread is not None and current_simulation_thread.is_alive():
        current_simulation_thread.join()

    current_simulation_thread = threading.Thread(target=simulation_thread, args=(fig, canvas))
    current_simulation_thread.start()


fig = Figure(figsize=(15, 5), dpi=100)  # Größe ändern, um Diagramme besser zu "fitten"
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

start_button = tk.Button(root, text="Start", command=lambda: main(fig, canvas))
start_button.pack()

# Dropdown-Liste für Sommer/Winter
season_label = tk.Label(root, text="Saison:")
season_label.pack()
season_combobox = ttk.Combobox(root, values=["Sommer", "Winter"], state="readonly")
season_combobox.current(0)  # Standardwert ist "Sommer"
season_combobox.pack()
summer.set(True)

def season_changed(event):
    if season_combobox.get() == "Sommer":
        summer.set(True)
    else:
        summer.set(False)

season_combobox.bind("<<ComboboxSelected>>", season_changed)

# Checkbox für Semesterferien
semester_ferien_checkbutton = tk.Checkbutton(root, text="Semesterferien", variable=semester_ferien)
semester_ferien_checkbutton.pack()

# Dropdown-Liste für Biersorten
beer_label = tk.Label(root, text="Biersorte im Angebot:")
beer_label.pack()
beer_combobox = ttk.Combobox(root, values=["Becks", "Landskron", "Hasseröder", "FeldSchlößchen", "Helles"], state="readonly", textvariable=selected_beer)
beer_combobox.current(0)  # Standardwert ist "Becks"
beer_combobox.pack()

root.mainloop()
