import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\nOperação inválida! Você não tem saldo suficiente.")

        elif valor > 0:
            self._saldo -= valor
            print("\n=== Saque realizado com sucesso! ===")
            return True

        else:
            print("\nOperação inválida! O valor informado é inválido.")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== Depósito realizado com sucesso! ===")
        else:
            print("\nOperação inválida! O valor informado é inválido.")
            return False

        return True
    
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\nOperação inválida! O valor do saque excede o limite.")

        elif excedeu_saques:
            print("\nOperação inválida! Número máximo de saques excedido.")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%s"),
            }
        )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)   

menu = """
============== MENU ==============
      
[1] - Depositar
[2] - Sacar
[3] - Extrato
[4] - Novo Usuário
[5] - Nova Conta
[6] - Listagem de Contas
[0] - Sair

===================================
            Bem vindo(a)!

=> """
    
def deposito(usuarios):
    cpf = input("Informe o CPF do cliente: ")
    usuario = filtro_usuario(cpf, usuarios)

    if not usuario:
        print("\nUsuário não encontrado!")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_usuario(usuarios)
    if not conta:
        return

    usuario.realizar_transacao(conta, transacao)

def saque(usuarios):
    cpf = input("Informe o CPF do cliente: ")
    usuario = filtro_usuario(cpf, usuarios)

    if not usuario:
        print("\nUsuário não encontrado!")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_usuario(usuarios)
    if not conta:
        return

    usuario.realizar_transacao(conta, transacao)

def exibe_extrato(usuarios):
    cpf = input("Informe o CPF do cliente: ")
    usuario = filtro_usuario(cpf, usuarios)

    if not usuario:
        print("\nUsuário não encontrado!")
        return

    conta = recuperar_conta_usuario(usuarios)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")

def cria_usuario(usuarios):
    cpf = input("Informe o seu CPF (APENAS números): ")
    usuario = filtro_usuario(cpf, usuarios)

    if usuario:
        print("\nCPF já cadastrado!")
        return
     
    nome = input("Informe o nome completo: ")
    data_nasc = input("Informe sua data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe seu endereço (logradouro, número - bairro - cidade/sigla estado): ")

    usuario = PessoaFisica(nome=nome, data_nascimento=data_nasc, cpf=cpf, endereco=endereco)

    usuarios.append(usuario)

    print("\nUsuário criado com sucesso!")

def filtro_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario["cpf"] == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def recuperar_conta_usuario(usuarios):
    if not usuarios.contas:
        print("\nUsuário não possui conta no sistema!")
        return
    return usuarios.contas[0]
        
def cria_conta(contas, num_conta, usuarios):
    cpf = input("Informe o CPF do usuário: ")
    usuario = filtro_usuario(cpf, usuarios)

    if not usuario:
        print("\nUsuário não encontrado!")
        return
    conta = ContaCorrente.nova_conta(usuario=usuarios, numero=num_conta)
    usuarios.append(conta)
    usuario.contas.append(conta)

    print("\nConta criada com sucesso!")

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def main():
    usuarios = []
    contas = []


    while True:

        opcao = int(input(menu))

        if opcao == 1:
            deposito(usuarios)

        elif opcao == 2:
            saque(usuarios)
        
        elif opcao == 3:
            exibe_extrato(usuarios)
        
        elif opcao == 4:
            cria_usuario(usuarios)
        
        elif opcao == 5:
            num_conta = len(contas) + 1
            cria_conta(contas, num_conta, usuarios)

        elif opcao == 6:
            listar_contas(contas)

        elif opcao == 0:
            print("\nObrigado por utilizar nosso sistema!!")
            break

        else:
            print("\nOperação inválida, por favor selecione novamente a operação desejada.")

main()