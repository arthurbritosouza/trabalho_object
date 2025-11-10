import unittest

from rental_quote.calculator import RentalQuoteCalculator
from rental_quote.models import QuoteRequest, RentalPropertyType


class RentalQuoteCalculatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.calculator = RentalQuoteCalculator()

    def test_apartment_without_children_discount(self) -> None:
        request = QuoteRequest(
            property_type=RentalPropertyType.APARTMENT,
            bedrooms=1,
            has_children=False,
            contract_installments=5,
        )
        result = self.calculator.calculate(request)
        self.assertAlmostEqual(result.monthly_rent, 665.0)
        self.assertAlmostEqual(result.discounts, 35.0)

    def test_house_with_two_bedrooms_and_garage(self) -> None:
        request = QuoteRequest(
            property_type=RentalPropertyType.HOUSE,
            bedrooms=2,
            garage=True,
            contract_installments=3,
        )
        result = self.calculator.calculate(request)
        self.assertAlmostEqual(result.extras, 550.0)
        self.assertAlmostEqual(result.monthly_rent, 1450.0)
        self.assertEqual(result.contract_installments, 3)

    def test_studio_with_additional_parking_spots(self) -> None:
        request = QuoteRequest(
            property_type=RentalPropertyType.STUDIO,
            bedrooms=1,
            studio_parking_spots=4,
            contract_installments=5,
        )
        result = self.calculator.calculate(request)
        # 2 vagas por R$250 + 2 vagas extras por R$60 cada
        self.assertAlmostEqual(result.extras, 370.0)
        self.assertAlmostEqual(result.monthly_rent, 1570.0)


if __name__ == "__main__":
    unittest.main()
