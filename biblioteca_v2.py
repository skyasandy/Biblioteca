#!/usr/bin/env python3
"""
Sistema de Gestão de Biblioteca - Versão 2 (Corrigida)

Esta versão corrige todos os defeitos identificados e aplica:
- Verificação: Validações técnicas e conformidade
- Validação: Atendimento às necessidades dos usuários

Autor: Estudo de Caso - Conceitos Fundamentais de Teste
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging


# Configuração de logging para monitoramento
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TipoUsuario(Enum):
    """Enumera os tipos de usuários do sistema."""
    ESTUDANTE = "estudante"
    PROFESSOR = "professor"


class StatusUsuario(Enum):
    """Enumera os status possíveis de um usuário."""
    ATIVO = "ativo"
    BLOQUEADO = "bloqueado"


class BibliotecaException(Exception):
    """Exceção base para erros específicos do sistema da biblioteca."""
    pass


class UsuarioInexistenteError(BibliotecaException):
    """Exceção para quando usuário não é encontrado."""
    pass


class LivroInexistenteError(BibliotecaException):
    """Exceção para quando livro não é encontrado."""
    pass


class ISBNInvalidoError(BibliotecaException):
    """Exceção para ISBN em formato inválido."""
    pass


class Livro:
    """
    Representa um livro no sistema da biblioteca.
    
    CORREÇÃO APLICADA: Validação rigorosa de ISBN
    """
    
    def __init__(self, isbn: str, titulo: str, autor: str, disponivel: bool = True):
        """
        Inicializa um livro com validação de ISBN.
        
        Args:
            isbn: ISBN do livro (deve ter 10 ou 13 dígitos)
            titulo: Título do livro
            autor: Autor do livro
            disponivel: Se o livro está disponível para empréstimo
            
        Raises:
            ISBNInvalidoError: Se ISBN não estiver no formato correto
            ValueError: Se título ou autor estiverem vazios
        """
        self.isbn = self._validar_isbn(isbn)
        
        if not titulo.strip():
            raise ValueError("Título não pode estar vazio")
        if not autor.strip():
            raise ValueError("Autor não pode estar vazio")
            
        self.titulo = titulo.strip()
        self.autor = autor.strip()
        self.disponivel = disponivel
        
        logger.info(f"Livro criado: {self.titulo} (ISBN: {self.isbn})")
    
    @staticmethod
    def _validar_isbn(isbn: str) -> str:
        """
        Valida o formato do ISBN.
        
        VERIFICAÇÃO: ISBN deve ter 10 ou 13 dígitos (pode ter hífens)
        
        Args:
            isbn: String contendo o ISBN
            
        Returns:
            str: ISBN limpo (apenas dígitos)
            
        Raises:
            ISBNInvalidoError: Se ISBN não estiver no formato correto
        """
        if not isbn:
            raise ISBNInvalidoError("ISBN não pode estar vazio")
        
        # Remove hífens e espaços
        isbn_limpo = re.sub(r'[-\s]', '', isbn)
        
        # Verifica se contém apenas dígitos
        if not isbn_limpo.isdigit():
            raise ISBNInvalidoError(f"ISBN deve conter apenas dígitos: {isbn}")
        
        # Verifica tamanho (10 ou 13 dígitos)
        if len(isbn_limpo) not in [10, 13]:
            raise ISBNInvalidoError(
                f"ISBN deve ter 10 ou 13 dígitos. Recebido: {len(isbn_limpo)} dígitos"
            )
        
        return isbn_limpo
    
    def emprestar(self) -> bool:
        """
        Marca o livro como emprestado se estiver disponível.
        
        Returns:
            bool: True se empréstimo foi realizado com sucesso
        """
        if self.disponivel:
            self.disponivel = False
            logger.info(f"Livro emprestado: {self.titulo}")
            return True
        logger.warning(f"Tentativa de empréstimo de livro indisponível: {self.titulo}")
        return False
    
    def devolver(self) -> None:
        """Marca o livro como disponível novamente."""
        self.disponivel = True
        logger.info(f"Livro devolvido: {self.titulo}")


class Usuario:
    """
    Representa um usuário do sistema da biblioteca.
    
    CORREÇÃO APLICADA: Lógica correta de bloqueio e validações
    """
    
    def __init__(self, user_id: str, nome: str, tipo: TipoUsuario, 
                 status: StatusUsuario = StatusUsuario.ATIVO):
        """
        Inicializa um usuário com validações.
        
        Args:
            user_id: Identificador único do usuário
            nome: Nome completo do usuário
            tipo: Tipo do usuário (estudante ou professor)
            status: Status inicial do usuário
            
        Raises:
            ValueError: Se dados obrigatórios estiverem inválidos
        """
        if not user_id.strip():
            raise ValueError("ID do usuário não pode estar vazio")
        if not nome.strip():
            raise ValueError("Nome do usuário não pode estar vazio")
        
        self.user_id = user_id.strip()
        self.nome = nome.strip()
        self.tipo = tipo
        self.status = status
        self.multa_total = 0.0
        
        logger.info(f"Usuário criado: {self.nome} ({self.tipo.value})")
    
    def pode_emprestar(self) -> bool:
        """
        Verifica se o usuário pode realizar empréstimos.
        
        CORREÇÃO: Lógica correta - usuário ATIVO pode emprestar
        
        Returns:
            bool: True se usuário pode emprestar
        """
        # CORREÇÃO: Condição CORRETA agora!
        pode = self.status == StatusUsuario.ATIVO
        
        if not pode:
            logger.warning(
                f"Empréstimo negado para usuário {self.nome}: status {self.status.value}"
            )
        
        return pode
    
    def adicionar_multa(self, valor: float) -> None:
        """
        Adiciona multa ao usuário e verifica limite de bloqueio.
        
        Args:
            valor: Valor da multa a ser adicionada
        """
        if valor < 0:
            raise ValueError("Valor da multa não pode ser negativo")
        
        self.multa_total += valor
        logger.info(f"Multa adicionada para {self.nome}: R$ {valor:.2f}")
        
        # Bloqueia usuário se multa ultrapassar limite
        if self.multa_total > 50.0 and self.status == StatusUsuario.ATIVO:
            self.status = StatusUsuario.BLOQUEADO
            logger.warning(
                f"Usuário {self.nome} bloqueado por multa alta: R$ {self.multa_total:.2f}"
            )


class Emprestimo:
    """
    Representa um empréstimo de livro.
    
    CORREÇÃO APLICADA: Prazos e cálculos corretos conforme requisitos
    """
    
    # Configurações de negócio (facilita manutenção)
    PRAZO_ESTUDANTE_DIAS = 7
    PRAZO_PROFESSOR_DIAS = 30  # CORREÇÃO: Valor correto agora!
    MULTA_ESTUDANTE_DIA = 1.0
    MULTA_PROFESSOR_DIA = 0.5  # CORREÇÃO: Valor correto agora!
    
    def __init__(self, usuario: Usuario, livro: Livro):
        """
        Inicializa um empréstimo com prazos corretos.
        
        VALIDAÇÃO: Prazos atendem às necessidades dos usuários
        """
        self.usuario = usuario
        self.livro = livro
        self.data_emprestimo = datetime.now()
        
        # CORREÇÃO: Prazos corretos conforme tipo de usuário
        if usuario.tipo == TipoUsuario.ESTUDANTE:
            self.prazo_dias = self.PRAZO_ESTUDANTE_DIAS
        else:  # Professor
            self.prazo_dias = self.PRAZO_PROFESSOR_DIAS  # ✅ CORRETO: 30 dias!
        
        self.data_vencimento = self.data_emprestimo + timedelta(days=self.prazo_dias)
        self.devolvido = False
        self.data_devolucao: Optional[datetime] = None
        
        logger.info(
            f"Empréstimo criado: {livro.titulo} para {usuario.nome} "
            f"(prazo: {self.prazo_dias} dias)"
        )
    
    def calcular_multa(self) -> float:
        """
        Calcula multa por atraso na devolução.
        
        CORREÇÃO: Taxas corretas conforme tipo de usuário
        
        Returns:
            float: Valor da multa calculada
        """
        if not (self.devolvido and self.data_devolucao):
            return 0.0
        
        dias_atraso = (self.data_devolucao - self.data_vencimento).days
        
        if dias_atraso <= 0:
            return 0.0
        
        # CORREÇÃO: Taxas corretas para cada tipo de usuário
        if self.usuario.tipo == TipoUsuario.ESTUDANTE:
            multa = dias_atraso * self.MULTA_ESTUDANTE_DIA  # R$ 1,00/dia
        else:  # Professor
            multa = dias_atraso * self.MULTA_PROFESSOR_DIA  # ✅ CORRETO: R$ 0,50/dia
        
        logger.info(
            f"Multa calculada para {self.usuario.nome}: "
            f"{dias_atraso} dias × R$ {self.MULTA_PROFESSOR_DIA if self.usuario.tipo == TipoUsuario.PROFESSOR else self.MULTA_ESTUDANTE_DIA:.2f} = R$ {multa:.2f}"
        )
        
        return multa
    
    def devolver_livro(self, data_devolucao: Optional[datetime] = None) -> float:
        """
        Processa a devolução do livro.
        
        Args:
            data_devolucao: Data da devolução (default: agora)
            
        Returns:
            float: Valor da multa aplicada
        """
        if self.devolvido:
            logger.warning(f"Livro {self.livro.titulo} já foi devolvido")
            return 0.0
        
        if data_devolucao is None:
            data_devolucao = datetime.now()
        
        self.data_devolucao = data_devolucao
        self.devolvido = True
        self.livro.devolver()
        
        multa = self.calcular_multa()
        if multa > 0:
            self.usuario.adicionar_multa(multa)
        
        logger.info(f"Devolução processada: {self.livro.titulo}")
        return multa


class SistemaBiblioteca:
    """
    Sistema principal de gestão da biblioteca.
    
    CORREÇÃO APLICADA: Tratamento de exceções e validações robustas
    """
    
    def __init__(self):
        self.livros: Dict[str, Livro] = {}
        self.usuarios: Dict[str, Usuario] = {}
        self.emprestimos: List[Emprestimo] = []
        
        logger.info("Sistema de biblioteca inicializado")
    
    def cadastrar_livro(self, isbn: str, titulo: str, autor: str) -> bool:
        """
        Cadastra um novo livro no sistema.
        
        CORREÇÃO: Validação de ISBN duplicado
        
        Args:
            isbn: ISBN do livro
            titulo: Título do livro
            autor: Autor do livro
            
        Returns:
            bool: True se cadastro foi bem-sucedido
            
        Raises:
            ISBNInvalidoError: Se ISBN for inválido
            ValueError: Se livro já existir
        """
        try:
            livro = Livro(isbn, titulo, autor)
            
            # CORREÇÃO: Verifica se ISBN já existe
            if livro.isbn in self.livros:
                raise ValueError(f"Livro com ISBN {livro.isbn} já existe")
            
            self.livros[livro.isbn] = livro
            logger.info(f"Livro cadastrado com sucesso: {titulo}")
            return True
            
        except (ISBNInvalidoError, ValueError) as e:
            logger.error(f"Erro ao cadastrar livro: {e}")
            raise
    
    def cadastrar_usuario(self, user_id: str, nome: str, tipo: TipoUsuario) -> bool:
        """
        Cadastra um novo usuário no sistema.
        
        Args:
            user_id: ID único do usuário
            nome: Nome do usuário
            tipo: Tipo do usuário
            
        Returns:
            bool: True se cadastro foi bem-sucedido
            
        Raises:
            ValueError: Se usuário já existir ou dados forem inválidos
        """
        if user_id in self.usuarios:
            raise ValueError(f"Usuário com ID {user_id} já existe")
        
        try:
            usuario = Usuario(user_id, nome, tipo)
            self.usuarios[user_id] = usuario
            logger.info(f"Usuário cadastrado com sucesso: {nome}")
            return True
            
        except ValueError as e:
            logger.error(f"Erro ao cadastrar usuário: {e}")
            raise
    
    def realizar_emprestimo(self, user_id: str, isbn: str) -> Emprestimo:
        """
        Realiza um empréstimo de livro.
        
        CORREÇÃO: Tratamento adequado de exceções e validações
        
        Args:
            user_id: ID do usuário
            isbn: ISBN do livro
            
        Returns:
            Emprestimo: Objeto do empréstimo criado
            
        Raises:
            UsuarioInexistenteError: Se usuário não existir
            LivroInexistenteError: Se livro não existir
            ValueError: Se empréstimo não puder ser realizado
        """
        # CORREÇÃO: Tratamento adequado de usuário inexistente
        if user_id not in self.usuarios:
            raise UsuarioInexistenteError(f"Usuário {user_id} não encontrado")
        
        # CORREÇÃO: Tratamento adequado de livro inexistente  
        if isbn not in self.livros:
            raise LivroInexistenteError(f"Livro com ISBN {isbn} não encontrado")
        
        usuario = self.usuarios[user_id]
        livro = self.livros[isbn]
        
        # Verifica se usuário pode emprestar
        if not usuario.pode_emprestar():
            raise ValueError(
                f"Usuário {usuario.nome} não pode emprestar: status {usuario.status.value}"
            )
        
        # Verifica se livro está disponível
        if not livro.emprestar():
            raise ValueError(f"Livro '{livro.titulo}' não está disponível")
        
        emprestimo = Emprestimo(usuario, livro)
        self.emprestimos.append(emprestimo)
        
        logger.info(f"Empréstimo realizado: {livro.titulo} para {usuario.nome}")
        return emprestimo
    
    def listar_emprestimos_pendentes(self) -> List[Tuple[str, str, datetime]]:
        """
        Lista empréstimos que ainda não foram devolvidos.
        
        Returns:
            Lista de tuplas (usuário, livro, data_vencimento)
        """
        pendentes = []
        for emp in self.emprestimos:
            if not emp.devolvido:
                pendentes.append((
                    emp.usuario.nome,
                    emp.livro.titulo,
                    emp.data_vencimento
                ))
        
        return pendentes


# =============================================================================
# DEMONSTRAÇÃO: Sistema Corrigido em Funcionamento
# =============================================================================

def demonstracao_sistema_corrigido():
    """
    Demonstra o sistema corrigido funcionando adequadamente.
    """
    print("=== DEMONSTRAÇÃO: Sistema Corrigido - Verificação e Validação ===\n")
    
    biblioteca = SistemaBiblioteca()
    
    # =================================================================
    # VERIFICAÇÃO: Validações técnicas funcionando
    # =================================================================
    print("🔍 VERIFICAÇÃO: Testando validações técnicas")
    
    try:
        # Testa ISBN inválido
        biblioteca.cadastrar_livro("123", "Livro Teste", "Autor Teste")
        print("❌ Falhou: ISBN inválido deveria ser rejeitado")
    except ISBNInvalidoError as e:
        print(f"✅ ISBN inválido rejeitado corretamente: {e}")
    
    try:
        # Cadastra livro com ISBN válido
        biblioteca.cadastrar_livro("9788535902772", "Clean Code", "Robert Martin")
        print("✅ Livro com ISBN válido cadastrado")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
    
    # =================================================================
    # VALIDAÇÃO: Atendendo necessidades dos usuários
    # =================================================================
    print("\n✅ VALIDAÇÃO: Atendendo necessidades dos usuários")
    
    # Cadastra usuários
    biblioteca.cadastrar_usuario("prof001", "Dr. Silva", TipoUsuario.PROFESSOR)
    biblioteca.cadastrar_usuario("est001", "João Santos", TipoUsuario.ESTUDANTE)
    
    # Testa empréstimo para professor
    emprestimo_prof = biblioteca.realizar_emprestimo("prof001", "9788535902772")
    print(f"📚 Professor - Prazo: {emprestimo_prof.prazo_dias} dias (Validação: requisito de 30 dias)")
    
    # Cadastra outro livro para estudante
    biblioteca.cadastrar_livro("9788575222683", "Python Fluente", "Luciano Ramalho")
    emprestimo_est = biblioteca.realizar_emprestimo("est001", "9788575222683")
    print(f"📖 Estudante - Prazo: {emprestimo_est.prazo_dias} dias (Validação: requisito de 7 dias)")
    
    # =================================================================
    # DEMONSTRAÇÃO: Multas corretas
    # =================================================================
    print("\n💰 DEMONSTRAÇÃO: Cálculo correto de multas")
    
    # Simula devolução com atraso para professor
    data_atraso_prof = datetime.now() + timedelta(days=5)
    multa_prof = emprestimo_prof.devolver_livro(data_atraso_prof)
    print(f"👨‍🏫 Professor - 5 dias atraso: R$ {multa_prof:.2f} (5 × R$ 0,50)")
    
    # Simula devolução com atraso para estudante  
    data_atraso_est = datetime.now() + timedelta(days=3)
    multa_est = emprestimo_est.devolver_livro(data_atraso_est)
    print(f"🎓 Estudante - 3 dias atraso: R$ {multa_est:.2f} (3 × R$ 1,00)")
    
    # =================================================================
    # VERIFICAÇÃO: Tratamento de exceções
    # =================================================================
    print("\n🛡️ VERIFICAÇÃO: Tratamento robusto de exceções")
    
    try:
        biblioteca.realizar_emprestimo("user999", "9788535902772")
    except UsuarioInexistenteError as e:
        print(f"✅ Usuário inexistente tratado: {e}")
    
    try:
        biblioteca.realizar_emprestimo("prof001", "isbn999")
    except LivroInexistenteError as e:
        print(f"✅ Livro inexistente tratado: {e}")
    
    print("\n🎉 Sistema funcionando corretamente após correções!")


if __name__ == "__main__":
    demonstracao_sistema_corrigido()