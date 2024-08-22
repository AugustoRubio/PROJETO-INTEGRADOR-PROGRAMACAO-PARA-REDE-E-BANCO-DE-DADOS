def gerarLista():
    lista = []
    quantidade = int(input("Informe a quantidade de elementos: "))
    arquivo = open("C:\\Users\\AugustoRubio\\Downloads\\este.txt", "w")

    quantidade-=1
    while quantidade >=0:
        lista.append(str(quantidade)+"\n")
        quantidade-=1

    arquivo.writelines(lista)
    arquivo.close()


gerarLista()