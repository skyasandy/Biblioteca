#!/usr/bin/env python3
"""
Sistema de Gestão de Biblioteca - Versão 1 (com problemas intencionais)

Este código contém erros propositais para demonstrar a cadeia causal:
Erro → Defeito → Falha → Incidente

Autor: Estudo de Caso - Conceitos Fundamentais de Teste
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum


class TipoUsuario(Enum):
    """Enumera os tipos de usuários do sistema."""
    ESTUDANTE = "estudante"
    PROFESSOR = "professor"


class StatusUsuario(Enum):
    """Enumera os status possíveis de um usuário."""
    ATIVO = "ativo"
    BLOQUEADO = "bloqueado"


class Livro:
    """
    Representa um livro no sistema da biblioteca.
    
    ERRO INTENCIONAL 1: Falta de validação adequada do ISBN
    """
    
    def __init__(self, isbn: str, titulo: str, autor: str, disponivel: bool = True):
        # DEFEITO: ISBN não é validado adequately
        # Um ISBN deve ter 10 ou 13 dígitos, mas não estamos verificando
        self.isbn = isbn  # Aqui está o DEFEITO
        self.titulo = titulo
        self.autor = autor
        self.disponivel = disponivel
    
    def emprestar(self) -> bool:
        """
        Marca o livro como emprestado.
        
        Returns:
            bool: True se empréstimo foi realizado com sucesso
        """
        if self.disponivel:
            self.disponivel = False
            return True
        return False
    
    def devolver(self) -> None:
        """Marca o livro como disponível novamente."""
        self.disponivel = True


class Usuario:
    """
    Representa um usuário do sistema da biblioteca.
    
    ERRO INTENCIONAL 2: Lógica incorreta na validação de bloqueio
    """
    
    def __init__(self, user_id: str, nome: str, tipo: TipoUsuario, 
                 status: StatusUsuario = StatusUsuario.ATIVO):
        self.user_id = user_id
        self.nome = nome
        self.tipo = tipo
        self.status = status
        self.multa_total = 0.0
    
    def pode_emprestar(self) -> bool:
        """
        Verifica se o usuário pode realizar empréstimos.
        
        DEFEITO: Lógica de bloqueio está invertida!
        O programador confundiu == com !=
        """
        # DEFEITO CRÍTICO: Esta condição está ERRADA!
        # Deveria ser: self.status == StatusUsuario.ATIVO
        return self.status == StatusUsuario.BLOQUEADO  # ❌ DEFEITO!
    
    def adicionar_multa(self, valor: float) -> None:
        """Adiciona multa ao usuário."""
        self.multa_total += valor
        
        # DEFEITO: Limite de bloqueio por multa mal implementado
        if self.multa_total > 50.0:  # Bloqueia com multa alta
            self.status = StatusUsuario.BLOQUEADO


class Emprestimo:
    """
    Representa um empréstimo de livro.
    
    ERRO INTENCIONAL 3: Cálculo incorreto de multa
    """
    
    def __init__(self, usuario: Usuario, livro: Livro):
        self.usuario = usuario
        self.livro = livro
        self.data_emprestimo = datetime.now()
        
        # DEFEITO: Cálculo de prazo com lógica errada para professores
        if usuario.tipo == TipoUsuario.ESTUDANTE:
            self.prazo_dias = 7
        else:  # Professor
            # DEFEITO: Número errado de dias para professor!
            # Requisito era 30 dias, mas programador colocou 3!
            self.prazo_dias = 3  # ❌ DEFEITO! Deveria ser 30
        
        self.data_vencimento = self.data_emprestimo + timedelta(days=self.prazo_dias)
        self.devolvido = False
        self.data_devolucao: Optional[datetime] = None
    
    def calcular_multa(self) -> float:
        """
        Calcula multa por atraso na devolução.
        
        DEFEITO: Taxa de multa incorreta para professores
        """
        if self.devolvido and self.data_devolucao:
            dias_atraso = (self.data_devolucao - self.data_vencimento).days
            
            if dias_atraso > 0:
                if self.usuario.tipo == TipoUsuario.ESTUDANTE:
                    return dias_atraso * 1.0  # Correto: R$ 1,00 por dia
                else:
                    # DEFEITO: Taxa errada para professor!
                    # Deveria ser 0.50, mas está 5.0!
                    return dias_atraso * 5.0  # ❌ DEFEITO! Deveria ser 0.50
        
        return 0.0
    
    def devolver_livro(self, data_devolucao: datetime = None) -> float:
        """
        Processa a devolução do livro.
        
        Returns:
            float: Valor da multa aplicada
        """
        if data_devolucao is None:
            data_devolucao = datetime.now()
        
        self.data_devolucao = data_devolucao
        self.devolvido = True
        self.livro.devolver()
        
        multa = self.calcular_multa()
        if multa > 0:
            self.usuario.adicionar_multa(multa)
        
        return multa


class SistemaBiblioteca:
    """
    Sistema principal de gestão da biblioteca.
    
    ERRO INTENCIONAL 4: Falta de tratamento de exceções
    """
    
    def __init__(self):
        self.livros: Dict[str, Livro] = {}
        self.usuarios: Dict[str, Usuario] = {}
        self.emprestimos: List[Emprestimo] = []
    
    def cadastrar_livro(self, isbn: str, titulo: str, autor: str) -> bool:
        """
        Cadastra um novo livro no sistema.
        
        DEFEITO: Não valida ISBN duplicado adequadamente
        """
        # DEFEITO: Não verifica se ISBN já existe!
        # Permite cadastros duplicados
        livro = Livro(isbn, titulo, autor)
        self.livros[isbn] = livro  # Sobrescreve livros existentes!
        return True
    
    def cadastrar_usuario(self, user_id: str, nome: str, tipo: TipoUsuario) -> bool:
        """Cadastra um novo usuário no sistema."""
        if user_id in self.usuarios:
            return False  # Usuário já existe
        
        usuario = Usuario(user_id, nome, tipo)
        self.usuarios[user_id] = usuario
        return True
    
    def realizar_emprestimo(self, user_id: str, isbn: str) -> Optional[Emprestimo]:
        """
        Realiza um empréstimo de livro.
        
        DEFEITO: Não trata casos de usuário/livro inexistente
        """
        # DEFEITO: Não verifica se usuário existe!
        # Pode causar KeyError (exceção não tratada)
        usuario = self.usuarios[user_id]  # ❌ Possível exceção!
        
        # DEFEITO: Não verifica se livro existe!
        livro = self.livros[isbn]  # ❌ Possível exceção!
        
        # Verifica se usuário pode emprestar
        if not usuario.pode_emprestar():
            return None  # Usuário bloqueado (mas lógica está invertida!)
        
        # Verifica se livro está disponível
        if not livro.emprestar():
            return None  # Livro não disponível
        
        emprestimo = Emprestimo(usuario, livro)
        self.emprestimos.append(emprestimo)
        return emprestimo


# =============================================================================
# DEMONSTRAÇÃO PRÁTICA: Como os DEFEITOS geram FALHAS e INCIDENTES
# =============================================================================

def demonstracao_cadeia_causal():
    """
    Demonstra como erros no código geram defeitos, 
    que causam falhas, que resultam em incidentes.
    """
    print("=== DEMONSTRAÇÃO: Cadeia Erro → Defeito → Falha → Incidente ===\n")
    
    # Inicializa o sistema
    biblioteca = SistemaBiblioteca()
    
    # Cadastra livros e usuários
    biblioteca.cadastrar_livro("123", "Python para Iniciantes", "Autor X")
    biblioteca.cadastrar_usuario("prof001", "Dr. Silva", TipoUsuario.PROFESSOR)
    biblioteca.cadastrar_usuario("est001", "João Santos", TipoUsuario.ESTUDANTE)
    
    print("✅ Sistema inicializado com livros e usuários")
    
    # =================================================================
    # INCIDENTE 1: Usuário bloqueado consegue fazer empréstimo
    # =================================================================
    print("\n🚨 INCIDENTE 1: Lógica de bloqueio invertida")
    
    # Força bloqueio do usuário
    usuario_estudante = biblioteca.usuarios["est001"]
    usuario_estudante.status = StatusUsuario.BLOQUEADO
    print(f"📋 Status do estudante: {usuario_estudante.status.value}")
    
    # Tenta fazer empréstimo (deveria ser negado, mas será aprovado!)
    emprestimo = biblioteca.realizar_emprestimo("est001", "123")
    
    if emprestimo:
        print("❌ FALHA: Usuário BLOQUEADO conseguiu fazer empréstimo!")
        print("💸 INCIDENTE: Biblioteca perde controle sobre usuários inadimplentes")
    else:
        print("✅ Empréstimo negado corretamente")
    
    # =================================================================
    # INCIDENTE 2: Professor com prazo errado
    # =================================================================
    print("\n🚨 INCIDENTE 2: Prazo incorreto para professor")
    
    # Cadastra novo livro para testar com professor
    biblioteca.cadastrar_livro("456", "Metodologia Científica", "Autor Y")
    emprestimo_prof = biblioteca.realizar_emprestimo("prof001", "456")
    
    if emprestimo_prof:
        print(f"📅 Prazo para professor: {emprestimo_prof.prazo_dias} dias")
        print("❌ FALHA: Professor deveria ter 30 dias, mas tem apenas 3!")
        print("😡 INCIDENTE: Professores reclamam de prazo muito curto")
    
    # =================================================================
    # INCIDENTE 3: Multa exorbitante para professor
    # =================================================================
    print("\n🚨 INCIDENTE 3: Multa incorreta para professor")
    
    # Simula devolução com atraso
    data_futura = datetime.now() + timedelta(days=5)  # 5 dias de atraso
    multa = emprestimo_prof.devolver_livro(data_futura)
    
    print(f"💰 Multa calculada: R$ {multa:.2f}")
    print("❌ FALHA: Professor deveria pagar R$ 2,50 (5 dias × R$ 0,50)")
    print("💸 INCIDENTE: Professor é cobrado R$ 25,00 - valor abusivo!")
    
    # =================================================================
    # INCIDENTE 4: Sistema trava com dados inexistentes
    # =================================================================
    print("\n🚨 INCIDENTE 4: Sistema trava com exceção não tratada")
    
    try:
        # Tenta empréstimo com usuário inexistente
        biblioteca.realizar_emprestimo("user999", "123")
    except KeyError as e:
        print(f"💥 EXCEÇÃO: {type(e).__name__} - {e}")
        print("❌ FALHA: Sistema não trata usuário inexistente")
        print("🔥 INCIDENTE: Sistema da biblioteca trava durante atendimento")


if __name__ == "__main__":
    demonstracao_cadeia_causal()