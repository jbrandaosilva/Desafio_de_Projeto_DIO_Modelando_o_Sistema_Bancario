import datetime
from abc import ABC, abstractclassmethod, abstractproperty

class Cliente():
    def __init__(self,endereco):
        self.endereco = endereco
        self.contas = []
        
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)
        
    def adicionar_conta(self, conta):
        self.contas.append(conta)
        
class PessoaFisica(Cliente):
    def __init__(self, nome, endereco, data_nascimento, cpf):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf
    
class Conta():
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
    
    def sacar(self, operacao):
        saldo = self.saldo
        excedeu_saldo = operacao > saldo
        
        if excedeu_saldo:
            print("\nSaldo insuficiente!")
            
        elif operacao > 0:
            self.saldo -= operacao
            print ("\Operação realizado com sucesso!")
            return True
        
        else:
            print("\nFalha na operação! Valor digitado é inválido.")
            
        return False
        
    def depositar(self, operacao):
        if operacao > 0:
            self.saldo += operacao
            print("\nOperação realizada com sucesso!")
            return True
            
        else:
            print("\nFalha na operação! Valor digitado é inválido.")
            return False
            
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite = 500, limites_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limites_saques = limites_saques
        
    def sacar(self, operacao):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )
        excedeu_limite = operacao > self._limite
        excedeu_saques = numero_saques >= self._limites_saques
        
        if excedeu_limite:
            print("\nO valor desejada excede o limite de saque.")

        elif excedeu_saques:
            print("\nNúmero de saques diário excedido! Volte amanhã!")
            
        else:     
            return super().sacar(operacao)
        
        return False
    
    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            Conta:\t\t{self.numero}
            Cliente:\t{self.cliente.nome}
            """

class Historico():
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

def menu():
    menu = """
    ================ EXTRATO ================
    [1] Depositar
    [2] Sacar
    [3] Extrato
    [4] Criar usuário
    [5] Nova conta
    [6] Listar contas
    [0] Sair
    =========================================
    => """
    
    return input(menu)

def depositar(usuarios):
    cpf = input("Informe o CPF do cliente: ")
    usuario = consultar_usuario(cpf, usuarios)
    
    if not usuario:
        print("Cliente não encontrado!") 
        return

    valor = float(input("Informe o valor do depósito: "))
    operacao = Deposito(valor)
    
    conta = consultar_conta(usuario)
    
    if not conta:
        return
    
    usuario.realizar_transacao(conta, operacao)

def consultar_usuario(cpf, usuarios):
    consulta = [usuario for usuario in usuarios if usuario.cpf == cpf]
    return consulta[0] if consulta else None

def consultar_conta(usuario):
    if not usuario.contas:
        print("\nCliente não possui conta!")
        return

    return usuario.contas[0]

def sacar(usuarios):
    cpf = input("Informe o CPF do cliente: ")
    usuario = consultar_usuario(cpf, usuarios)
    
    if not usuario:
        print("Cliente não encontrado!") 
        return
    
    valor = float(input("Informe o valor do saque: "))
    operacao = Saque(valor)
    
    conta = consultar_conta(usuario)
    if not conta:
        return
    
    usuario.realizar_transacao(conta, operacao)

def exibir_extrato(usuarios):
    cpf = input("Informe o CPF do cliente: ")
    usuario = consultar_usuario(cpf, usuarios)
    
    if not usuario:
        print("Cliente não encontrado!") 
        return
    
    conta = consultar_conta(usuario)
    if not conta:
        return
    
    print("\n================ EXTRATO ================")
    operacoes = usuario.realizar_transacao
    extrato = ""
    
    if not operacoes:
        extrato="Não foram realizadas movimentações."
        
    else:
        for operacao in operacoes:
            extrato +=f"\n{operacao['tipo']}:\n\tR${operacao['valor']:.2f}"
            
    print(extrato)
    print(f"\nSaldo: R$ {conta.saldo:.2f}")
    print("==========================================")

def criar_usuario(usuarios):
    cpf = input("Informe o seu CPF (somente os números): ")
    usuario = consultar_usuario(cpf, usuarios)
    
    if usuario:
        print ("Usuário já é o nosso cliente!")
        return
    
    nome = input("Informe o seu nome completo: ")
    data_nascimento = input("Informe sua data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o seu endereço (logradouro, numero - bairro - cidade/sigla estado): ")
    
    usuario = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    
    usuarios.append(usuario)
    
    print("Usuário criado!")

def criar_conta(numero_conta, usuarios, contas):
    cpf = input("Informe o CPF do usuário: ")
    usuario = consultar_usuario(cpf, usuarios)

    if not usuario:
        print("Cliente não encontrado!") 
        return

    conta = ContaCorrente.nova_conta(cliente=usuario, numero=numero_conta)
    contas.append(conta)
    usuario.contas.append(conta)

    print("Conta criada!")

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(conta)
        
def main():
    usuarios = []
    contas = []
    
    while True:
        opcao = menu()
        
        if opcao == "1":
            depositar(usuarios)

        elif opcao == "2":
            sacar(usuarios)
            
        elif opcao == "3":
            exibir_extrato(usuarios)
            
        elif opcao == "4":
            criar_usuario(usuarios)
            
        elif opcao == "5":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, usuarios, contas)

        elif opcao == "6":
            listar_contas(contas)
            
        elif opcao == "0":
            break
        
        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")
                      
main()    