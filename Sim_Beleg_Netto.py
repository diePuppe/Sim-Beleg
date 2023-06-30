import simpy
import random

class BeerStore:
    def __init__(self, env):
        self.env = env
        self.store = simpy.Container(env, init=100, capacity=10000)  # Anzahl der Bierflaschen im Laden

    def buy_beer(self, amount):
        yield self.store.get(amount)


def customer(env, name, store):
    while True:
        
        # Kunde kommt in den Laden
        arrive = random.expovariate(1/5)  # Kunden kommen im Durchschnitt alle 5 Minuten
        yield env.timeout(arrive)

        # Kunde kauft Bier
        amount = random.randint(1, 6)  # Kunde kauft 1-6 Bierflaschen
        yield env.process(store.buy_beer(amount))
        
        count =+ 1
        print(count)
        if count > 10:
            print(f"Der Laden hat noch {store.store.level} Bier")
            count = 0

        # Kunde verlässt den Laden
        leave = random.expovariate(1/10)  # Kunde bleibt im Durchschnitt 10 Minuten im Laden
        yield env.timeout(leave)

def restock(env, store):
    while True:
        yield env.timeout(10)  # Prüfen Sie alle 10 Zeiteinheiten

        if store.store.level < random.randint(50,500):  # Simulation wann auffält das zu wenig Bier da ist bzw Standartbestellungen
            print(f"Restocking beer at time {env.now}")
            restore = random.randint(100, 500)
            yield store.store.put(500)  # Füllen Sie das Bier nach
            print(f"Finished restocking beer at time {env.now}")


def main():
    env = simpy.Environment()
    store = BeerStore(env)


    # Erzeugen von Kunden
    for i in range(20):
        env.process(customer(env, f"Customer {i}", store))




    # Bier nachfüllen
    env.process(restock(env, store))

    # Simulation starten
    env.run(until=10000)

if __name__ == "__main__":
    main()
