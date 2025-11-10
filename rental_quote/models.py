from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


class RentalPropertyType(Enum):
    """Enumeration of the supported property types."""

    APARTMENT = "apartment"
    HOUSE = "house"
    STUDIO = "studio"

    @classmethod
    def from_input(cls, value: str) -> "RentalPropertyType":
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized or normalized.startswith(member.value[0]):
                return member
        raise ValueError(f"Tipo de imóvel inválido: {value}")


@dataclass(frozen=True)
class RentalPricingRule:
    """Pricing rules associated with a property type."""

    property_type: RentalPropertyType
    base_price: float
    base_bedrooms: int
    extra_bedroom_cost: float = 0.0
    garage_cost: float = 0.0


@dataclass
class QuoteRequest:
    """Information provided by the customer to request a quote."""

    property_type: RentalPropertyType
    bedrooms: int = 1
    has_children: bool = True
    garage: bool = False
    studio_parking_spots: int = 0
    contract_installments: int = 5

    def validate(self) -> None:
        if self.property_type in {RentalPropertyType.APARTMENT, RentalPropertyType.HOUSE}:
            if self.bedrooms not in (1, 2):
                raise ValueError("Somente são permitidos imóveis com 1 ou 2 quartos.")
        elif self.property_type == RentalPropertyType.STUDIO:
            if self.bedrooms != 1:
                raise ValueError("Estúdios são considerados com um único ambiente (1 quarto).")
        if not 1 <= self.contract_installments <= 5:
            raise ValueError("O contrato pode ser parcelado em até 5 vezes.")
        if self.studio_parking_spots < 0:
            raise ValueError("Quantidade de vagas de estacionamento inválida.")


@dataclass
class QuoteResult:
    """Detailed result of the rental quote calculation."""

    monthly_rent: float
    discounts: float
    extras: float
    contract_total: float
    contract_installments: int

    def monthly_contract_installment(self) -> float:
        return self.contract_total / self.contract_installments

    def total_first_month(self) -> float:
        return self.monthly_rent + self.monthly_contract_installment()

    def build_monthly_breakdown(self, months: int = 12) -> List[dict]:
        breakdown = []
        contract_installment = self.monthly_contract_installment()
        for month in range(1, months + 1):
            contract_payment = contract_installment if month <= self.contract_installments else 0.0
            total_due = self.monthly_rent + contract_payment
            breakdown.append(
                {
                    "month": month,
                    "rent": round(self.monthly_rent, 2),
                    "contract": round(contract_payment, 2),
                    "total": round(total_due, 2),
                }
            )
        return breakdown


CONTRACT_FEE = 2000.0
CONTRACT_MAX_INSTALLMENTS = 5
