from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsuarioCriar(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)


class UsuarioResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr


class TokenResposta(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=20)


class UsuarioAtualizar(BaseModel):
    email: EmailStr | None = None
    senha_atual: str = Field(min_length=8, max_length=128)
    nova_senha: str | None = Field(default=None, min_length=8, max_length=128)


class RecuperacaoSenhaSolicitar(BaseModel):
    email: EmailStr


class RecuperacaoSenhaRedefinir(BaseModel):
    token: str = Field(min_length=20)
    nova_senha: str = Field(min_length=8, max_length=128)


class ContaFinanceiraCriar(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    banco: str = Field(min_length=1, max_length=100)
    tipo: Literal[
        "cartao_credito",
        "cartao_debito",
        "conta_corrente",
        "conta_poupanca",
        "dinheiro",
    ]


class ContaFinanceiraAtualizar(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    banco: str | None = Field(default=None, min_length=1, max_length=100)
    tipo: Literal[
        "cartao_credito",
        "cartao_debito",
        "conta_corrente",
        "conta_poupanca",
        "dinheiro",
    ] | None = None


class ContaFinanceiraResposta(ContaFinanceiraCriar):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    ativa: bool


class ReceitaCriar(BaseModel):
    descricao: str = Field(min_length=1, max_length=200)
    categoria: str = Field(min_length=1, max_length=80)
    valor: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    data: date
    conta_id: int
    observacoes: str | None = Field(default=None, max_length=500)


class ReceitaAtualizar(BaseModel):
    descricao: str | None = Field(default=None, min_length=1, max_length=200)
    categoria: str | None = Field(default=None, min_length=1, max_length=80)
    valor: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    data: date | None = None
    conta_id: int | None = None
    observacoes: str | None = Field(default=None, max_length=500)


class ReceitaResposta(ReceitaCriar):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    conta_id: int | None


class ParcelaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: int
    valor: Decimal
    data_vencimento: date
    status: str


class CompraCriar(BaseModel):
    descricao: str = Field(min_length=1, max_length=200)
    categoria: str = Field(min_length=1, max_length=80)
    valor_total: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    quantidade_parcelas: int = Field(default=1, gt=0, le=120)
    data_compra: date
    conta_id: int
    observacoes: str | None = Field(default=None, max_length=500)


class CompraAtualizar(BaseModel):
    descricao: str | None = Field(default=None, min_length=1, max_length=200)
    categoria: str | None = Field(default=None, min_length=1, max_length=80)
    valor_total: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    quantidade_parcelas: int | None = Field(default=None, gt=0, le=120)
    data_compra: date | None = None
    conta_id: int | None = None
    observacoes: str | None = Field(default=None, max_length=500)


class CompraResposta(CompraCriar):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    conta_id: int | None
    parcelas: list[ParcelaResposta]
