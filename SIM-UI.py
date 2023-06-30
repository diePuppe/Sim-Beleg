import tkinter as tk
import simpy
import random
import numpy as np

class BeerStore:
    def __init__(self, env, text_area):
        self.env = env
        self.store = simpy.Container(env, init=3610, capacity=10000)  # Anzahl der Bierflaschen im Laden am Anfang und wie viele am Ende maximal im Laden sein können
        self.text_area = text_area
        self.customers = 0
        self.total_beer_sold = 0

    def buy_beer(self, amount):
        self.total_beer_sold += amount
        yield self.store.get(amount)
        self.customers -= 1
        self.update_ui()

    def add_customer(self):
        self.customers += 1
        self.update_ui()

    def update_ui(self):
        self.text_area.delete('1.0', tk.END)
        self.text_area.insert(tk.END, f'Time: {self.env.now}\n')
        self.text_area.insert(tk.END, f'Customers: {self.customers}\n')
        self.text_area.insert(tk.END, f'Total beer sold: {self.total_beer_sold}\n')
        self.text_area.insert(tk.END, f'Beer remaining: {self.store.level}\n')

def customer(env, store, temp):
    while True:
        store.add_customer()
        if temp < 15:                       # Kunden kaufen mehr Bier wenn es warm ist
            amount = random.randint(1, 3)
        elif temp < 25 & temp > 15:
            amount = random.randint(2, 6)
        else:
            amount = random.randint(4, 10) 
        
        # Kunde kommt in den Laden
        arrive_rate = customer_arrival_rate(env.now)
        arrive = random.expovariate(arrive_rate)
        yield env.timeout(arrive) #zieht die Zeit ab

        # Kunde kauft Bier
        yield env.process(store.buy_beer(amount))

def restock(env, store):
    while True:
        yield env.timeout(10)  # Prüfen Sie alle 10 Zeiteinheiten

        if store.store.level < random.randint(50,2000):  # Simulation wann auffält das zu wenig Bier da ist bzw Standartbestellungen
            restore = random.randint(20, 3610) #Anzahl von einer Palette Bier
            yield store.store.put(restore)  # Bier nachfüllen
        store.update_ui()

def customer_arrival_rate(t):

    # Diese Funktion gibt die Kundenankunftsrate zu einer bestimmten Zeit t zurück
    # Es ist so gestaltet, dass die Rate zwischen 7 und 11 Uhr niedrig ist, 
    # zwischen 11 und 18 Uhr hoch und danach wieder niedrig bis 22 Uhr

    # Konvertiert die Simulationszeit in "Echtzeit"
    real_time = (t % 1440) / 1440.0 * 24.0 

    # Normalverteilungsparameter
    mean_morning = 9.0
    std_dev_morning = 1.0
    mean_afternoon = 14.5
    std_dev_afternoon = 2.5
    mean_evening = 20.0
    std_dev_evening = 2.0

    # Die Kundenankunftsrate ist proportional zur Wahrscheinlichkeitsdichtefunktion der Normalverteilung
    morning = np.exp(-(real_time - mean_morning)**2 / (2 * std_dev_morning**2))
    afternoon = np.exp(-(real_time - mean_afternoon)**2 / (2 * std_dev_afternoon**2))
    evening = np.exp(-(real_time - mean_evening)**2 / (2 * std_dev_evening**2))

    # Kombiniert die Raten von morgens, nachmittags und abends
    rate = morning + afternoon + evening

    # Normiert die Rate, sodass sie nie kleiner als 0.1 ist (um zu vermeiden, dass es zu Zeiten mit sehr wenigen Kundenankünften zu lange dauert)
    rate = max(rate, 0.1)

    return rate

def main(text_area):
    
    text_area.delete('1.0', tk.END)

    env = simpy.Environment()
    store = BeerStore(env, text_area)
    temp = random.randint(5,36) # Temperatur wird zufällig generiert
    students= random.randint(1,301) # 171 Tage sind Studenten in der Uni.

    

    # Erzeugen von Kunden
    for i in range(20):
        env.process(customer(env, store, temp))

    # Bier nachfüllen
    env.process(restock(env, store))

    # Simulation starten
    env.run(until=1440)

root = tk.Tk()
text_area = tk.Text(root)
text_area.pack()

# Erstellen Sie eine Schaltfläche und binden Sie sie an die Funktion main
start_button = tk.Button(root, text="Neustart", command=lambda: main(text_area))
start_button.pack()

root.mainloop()
