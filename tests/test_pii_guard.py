"""Tests for the PII gate (src/utils/pii_guard.py)."""
from utils.pii_guard import detect_pii


class TestNir:
    def test_detects_valid_nir(self):
        text = "Salarié n° 1 85 12 75 108 234 81, référence dossier."
        assert "nir" in detect_pii(text)

    def test_detects_valid_nir_without_spaces(self):
        assert "nir" in detect_pii("Voici le NIR: 185127510823481 pour le dossier.")

    def test_ignores_invalid_checksum(self):
        # same digits as the valid fixture above, wrong 2-digit key
        text = "Référence 185127510823482 dans le document."
        assert "nir" not in detect_pii(text)

    def test_handles_corsica_department_code(self):
        text = "Identifiant 1851219108234 41 sur la fiche."
        assert "nir" in detect_pii(text)

    def test_no_false_positive_on_plain_paragraph(self):
        text = "Monod kinetics describe microbial growth rate as a function of substrate concentration. " * 5
        assert detect_pii(text) == []


class TestIban:
    def test_detects_valid_french_iban(self):
        assert "iban" in detect_pii("Virement vers FR7630006000011234567890189 avant vendredi.")

    def test_detects_valid_iban_with_spaces(self):
        assert "iban" in detect_pii("IBAN : DE89 3704 0044 0532 0130 00")

    def test_ignores_invalid_checksum(self):
        assert "iban" not in detect_pii("Compte FR7630006000011234567890188 (une erreur de frappe).")

    def test_no_false_positive_on_random_alnum(self):
        assert detect_pii("Ref commande AB12CD34EF56GH78IJ90 non trouvée.") == []


class TestCreditCard:
    def test_detects_luhn_valid_card(self):
        assert "credit_card" in detect_pii("Carte enregistrée : 4111 1111 1111 1111")

    def test_ignores_luhn_invalid_number(self):
        assert "credit_card" not in detect_pii("Numéro de suivi : 1234567890123456")

    def test_no_false_positive_on_short_number(self):
        assert detect_pii("Ligne 4111111111 dans le fichier de config.") == []

    def test_ignores_long_digit_runs_inside_code_blocks(self):
        text = "Résultat :\n```\nJoint position: [1.3509329557418823, -1.189529299736023]\n```"
        assert detect_pii(text) == []

    def test_ignores_hex_dump_inside_code_block(self):
        text = "Désassemblage :\n```asm\n0000000000000000 <add_float>:\n```"
        assert detect_pii(text) == []

    def test_ignores_sciencedirect_pii_identifier_in_url(self):
        # Elsevier's own "PII" (Publisher Item Identifier), not personal data.
        text = "Source : https://www.sciencedirect.com/science/article/pii/S0098135421004075"
        assert detect_pii(text) == []


class TestHrFiscalKeyword:
    def test_detects_payslip_keyword(self):
        assert "hr_fiscal_keyword" in detect_pii("Bulletin de paie - Décembre 2025")

    def test_detects_english_payslip(self):
        assert "hr_fiscal_keyword" in detect_pii("Employee Payslip for December")

    def test_detects_tax_notice_accent_insensitive(self):
        assert "hr_fiscal_keyword" in detect_pii("avis d'imposition 2025 joint")

    def test_no_false_positive_on_unrelated_text(self):
        assert detect_pii("Rapport mensuel sur la veille technologique.") == []


class TestDetectPii:
    def test_empty_and_none(self):
        assert detect_pii("") == []
        assert detect_pii(None) == []
        assert detect_pii("   ") == []

    def test_multiple_reasons_combined(self):
        text = "Bulletin de paie, NIR 185127510823481, IBAN FR7630006000011234567890189."
        reasons = detect_pii(text)
        assert set(reasons) == {"hr_fiscal_keyword", "nir", "iban"}

    def test_never_returns_the_matched_text(self):
        text = "Bulletin de paie de Jean Dupont, NIR 185127510823481."
        for reason in detect_pii(text):
            assert "185127510823481" not in reason
            assert "Dupont" not in reason
