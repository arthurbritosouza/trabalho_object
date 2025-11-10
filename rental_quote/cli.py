from __future__ import annotations

from datetime import datetime

from .calculator import RentalQuoteCalculator
from .csv_exporter import export_breakdown_to_csv
from .models import QuoteRequest, RentalPropertyType


def prompt_property_type() -> RentalPropertyType:
    options = {
        "a": RentalPropertyType.APARTMENT,
        "c": RentalPropertyType.HOUSE,
        "e": RentalPropertyType.STUDIO,
    }
    prompt = (
        "Escolha o tipo de imóvel:\n"
        "[A] Apartamento\n"
        "[C] Casa\n"
        "[E] Estúdio\n"
        "Opção: "
    )
    while True:
        choice = input(prompt).strip().lower()
        try:
            return options[choice]
        except KeyError:
            print("Opção inválida. Tente novamente.")


def prompt_yes_no(message: str, default: bool | None = None) -> bool:
    suffix = " [s/n]: " if default is None else (" [S/n]: " if default else " [s/N]: ")
    while True:
        answer = input(message + suffix).strip().lower()
        if not answer and default is not None:
            return default
        if answer in {"s", "sim"}:
            return True
        if answer in {"n", "nao", "não"}:
            return False
        print("Resposta inválida. Digite 's' para sim ou 'n' para não.")


def prompt_bedrooms(property_type: RentalPropertyType) -> int:
    if property_type == RentalPropertyType.STUDIO:
        return 1
    while True:
        value = input("Quantidade de quartos (1 ou 2): ").strip()
        if value in {"1", "2"}:
            return int(value)
        print("Informe 1 ou 2 quartos.")


def prompt_contract_installments() -> int:
    while True:
        value = input("Quantidade de parcelas para o contrato (1 a 5) [5]: ").strip()
        if not value:
            return 5
        if value.isdigit() and 1 <= int(value) <= 5:
            return int(value)
        print("Valor inválido. Informe um número entre 1 e 5.")


def prompt_studio_parking() -> int:
    while True:
        value = input("Quantidade de vagas de estacionamento desejadas (0 para nenhuma): ").strip()
        if value.isdigit():
            return int(value)
        print("Informe um número inteiro maior ou igual a zero.")


def run_cli() -> None:
    calculator = RentalQuoteCalculator()
    property_type = prompt_property_type()
    bedrooms = prompt_bedrooms(property_type)

    request = QuoteRequest(
        property_type=property_type,
        bedrooms=bedrooms,
        garage=False,
        has_children=True,
        studio_parking_spots=0,
        contract_installments=prompt_contract_installments(),
    )

    if property_type in {RentalPropertyType.APARTMENT, RentalPropertyType.HOUSE}:
        request.garage = prompt_yes_no("Deseja incluir vaga de garagem?", default=False)
    if property_type == RentalPropertyType.APARTMENT:
        request.has_children = prompt_yes_no("Existem crianças na residência?", default=True)
    if property_type == RentalPropertyType.STUDIO:
        request.studio_parking_spots = prompt_studio_parking()

    quote = calculator.calculate(request)

    print("\n===== ORÇAMENTO GERADO =====")
    print(f"Tipo de imóvel: {request.property_type.name.title()}")
    print(f"Valor base: R$ {calculator.catalog.get_rule(request.property_type).base_price:.2f}")
    print(f"Adicionais: R$ {quote.extras:.2f}")
    print(f"Descontos: R$ {quote.discounts:.2f}")
    print(f"Valor mensal do aluguel: R$ {quote.monthly_rent:.2f}")
    print(
        "Contrato: R$ "
        f"{quote.contract_total:.2f} em {quote.contract_installments} x de "
        f"R$ {quote.monthly_contract_installment():.2f}"
    )
    print(f"Total do primeiro mês: R$ {quote.total_first_month():.2f}")

    if prompt_yes_no("Deseja exportar as 12 parcelas para CSV?", default=False):
        breakdown = quote.build_monthly_breakdown(12)
        default_name = f"orcamento_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filename = input(f"Informe o nome do arquivo [default: {default_name}]: ").strip()
        path = export_breakdown_to_csv(breakdown, filename or default_name)
        print(f"Arquivo gerado em: {path.resolve()}")


if __name__ == "__main__":
    run_cli()
