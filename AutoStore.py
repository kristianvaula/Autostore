class Product:

    allProducts = {}

    def run(self):
        loop = True
        while loop:
            print("\n1: Legg til nye produkter til DataBasen")
            print("2: Fjern et produkt fra DataBasen")
            print("3: Skriv ut alle produktene fra DataBasen")
            print("4: Hent ut et spesifikt produkt")
            print("5: Gå ut av programmet\n")
            choice = int(input("Skriv inn hva du ønsker å gjøre\n"))

            if choice == 1:
                num = 0
                grense = int(input("Hvor mange produkter skal du registrere i systemet?\n"))

                def create_location(self):
                    x_count = int(input("X-count\n"))
                    y_count = int(input("Y-count\n"))
                    product = {
                        "X_count": x_count,
                        "Y_count": y_count
                    }
                    return product

                def create_name(self):
                    name = input("Product name\n")
                    return name

                while num <= (grense - 1):
                    self.allProducts.update({create_name(self): create_location(self)})
                    num = num + 1

                print("Produktene er lagt til i DataBasen\n")

            elif choice == 2:
                print(self.allProducts)
                name = input("Hvilket produkt ønsker du å fjerne?\n")
                self.allProducts.pop(name)

            elif choice == 3:
                print(self.allProducts)

            elif choice == 4:
                print(self.allProducts)
                prod = input("Hvilket product vil du hente ut?\n")
                pr = self.allProducts.get(prod)
                return pr["X_count"], pr["Y_count"]

            elif choice == 5:
                loop = False
