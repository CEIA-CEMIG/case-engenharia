from src.data.csv_to_gcp import CSVToGCP  # ajuste o import conforme seu path

if __name__ == "__main__":
    csv_path = "/home/evenicole/CEMIG/case-engenharia/tarifas/tarifas-homologadas-distribuidoras-energia-eletrica.csv"  # ex: "data/clientes.csv"
    loader = CSVToGCP()
    loader.run(csv_path)
