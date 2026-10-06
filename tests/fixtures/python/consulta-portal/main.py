from db import salvar
from portal import consultar


def run():
    for cnpj in ["00000000000100"]:
        salvar(cnpj, consultar(cnpj))


if __name__ == "__main__":
    run()
