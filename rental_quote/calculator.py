from __future__ import annotations

from dataclasses import dataclass

from .models import (
    CONTRACT_FEE,
    CONTRACT_MAX_INSTALLMENTS,
    QuoteRequest,
    QuoteResult,
    RentalPricingRule,
    RentalPropertyType,
)


@dataclass
class RentalCatalog:
    """Aggregates the pricing rules for all property types."""

    apartment: RentalPricingRule = RentalPricingRule(
        property_type=RentalPropertyType.APARTMENT,
        base_price=700.0,
        base_bedrooms=1,
        extra_bedroom_cost=200.0,
        garage_cost=300.0,
    )
    house: RentalPricingRule = RentalPricingRule(
        property_type=RentalPropertyType.HOUSE,
        base_price=900.0,
        base_bedrooms=1,
        extra_bedroom_cost=250.0,
        garage_cost=300.0,
    )
    studio: RentalPricingRule = RentalPricingRule(
        property_type=RentalPropertyType.STUDIO,
        base_price=1200.0,
        base_bedrooms=1,
    )

    def get_rule(self, property_type: RentalPropertyType) -> RentalPricingRule:
        if property_type == RentalPropertyType.APARTMENT:
            return self.apartment
        if property_type == RentalPropertyType.HOUSE:
            return self.house
        if property_type == RentalPropertyType.STUDIO:
            return self.studio
        raise ValueError(f"Tipo de imóvel não encontrado: {property_type}")


class RentalQuoteCalculator:
    """Calculates rental quotes based on the business rules."""

    def __init__(self, catalog: RentalCatalog | None = None) -> None:
        self.catalog = catalog or RentalCatalog()

    def calculate(self, request: QuoteRequest) -> QuoteResult:
        request.validate()
        rule = self.catalog.get_rule(request.property_type)

        extras = self._calculate_extras(rule, request)
        discounts = self._calculate_discounts(rule, request)
        monthly_rent = rule.base_price + extras - discounts

        return QuoteResult(
            monthly_rent=round(monthly_rent, 2),
            discounts=round(discounts, 2),
            extras=round(extras, 2),
            contract_total=CONTRACT_FEE,
            contract_installments=min(request.contract_installments, CONTRACT_MAX_INSTALLMENTS),
        )

    def _calculate_extras(self, rule: RentalPricingRule, request: QuoteRequest) -> float:
        extras = 0.0

        if request.property_type in {RentalPropertyType.APARTMENT, RentalPropertyType.HOUSE}:
            if request.bedrooms > rule.base_bedrooms:
                extras += rule.extra_bedroom_cost
            if request.garage:
                extras += rule.garage_cost
        elif request.property_type == RentalPropertyType.STUDIO:
            if request.studio_parking_spots > 0:
                # The first two spots form a bundle costing R$250
                extras += 250.0
                if request.studio_parking_spots > 2:
                    extras += (request.studio_parking_spots - 2) * 60.0
        return extras

    def _calculate_discounts(self, rule: RentalPricingRule, request: QuoteRequest) -> float:
        if request.property_type == RentalPropertyType.APARTMENT and not request.has_children:
            return rule.base_price * 0.05
        return 0.0
