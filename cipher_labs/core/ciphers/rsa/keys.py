import base64
import math
import xml.etree.ElementTree as ET
from dataclasses import dataclass

from .numtheory import generate_prime, mod_inverse
from .validators import DEFAULT_PUBLIC_EXPONENT, RSAKeyValidator

_FALLBACK_EXPONENTS = (65537, 257, 17, 5, 3)


def _int_to_b64(value: int) -> str:
    raw = value.to_bytes(max(1, (value.bit_length() + 7) // 8), "big")
    return base64.b64encode(raw).decode("ascii")


def _b64_to_int(text: str, tag: str) -> int:
    try:
        return int.from_bytes(base64.b64decode(text.strip(), validate=True), "big")
    except ValueError:
        raise ValueError(f"Поле <{tag}> містить некоректний Base64.") from None


@dataclass(frozen=True)
class RSAKey:
    """Ключ RSA. Відкритий ключ – (e, n), закритий – (d, n)"""
    n: int
    e: int
    d: int | None = None
    p: int | None = None
    q: int | None = None

    @property
    def has_private(self) -> bool:
        return self.d is not None

    @property
    def bits(self) -> int:
        return self.n.bit_length()

    @property
    def phi(self) -> int | None:
        if self.p is None or self.q is None:
            return None
        return (self.p - 1) * (self.q - 1)

    def public_key(self) -> "RSAKey":
        return RSAKey(n=self.n, e=self.e)

    def public_str(self) -> str:
        return f"{self.e}, {self.n}"

    def private_str(self) -> str:
        if self.d is None:
            raise ValueError("Закритий ключ невідомий.")
        return f"{self.d}, {self.n}"

    # Аналоги ToXmlString / FromXmlString з .NET
    def to_xml(self, include_private: bool = False) -> str:
        root = ET.Element("RSAKeyValue")
        ET.SubElement(root, "Modulus").text = _int_to_b64(self.n)
        ET.SubElement(root, "Exponent").text = _int_to_b64(self.e)
        if include_private:
            if self.d is None or self.p is None or self.q is None:
                raise ValueError("Для експорту закритого ключа потрібні p, q і d.")
            ET.SubElement(root, "P").text = _int_to_b64(self.p)
            ET.SubElement(root, "Q").text = _int_to_b64(self.q)
            ET.SubElement(root, "DP").text = _int_to_b64(self.d % (self.p - 1))
            ET.SubElement(root, "DQ").text = _int_to_b64(self.d % (self.q - 1))
            ET.SubElement(root, "InverseQ").text = _int_to_b64(mod_inverse(self.q, self.p))
            ET.SubElement(root, "D").text = _int_to_b64(self.d)
        return ET.tostring(root, encoding="unicode")

    @classmethod
    def from_xml(cls, xml_text: str) -> "RSAKey":
        if not isinstance(xml_text, str) or not xml_text.strip():
            raise ValueError("XML ключа порожній.")
        try:
            root = ET.fromstring(xml_text.strip())
        except ET.ParseError as err:
            raise ValueError(f"Некоректний XML ключа: {err}") from None
        if root.tag != "RSAKeyValue":
            raise ValueError("Очікувався елемент <RSAKeyValue>.")

        def field(tag: str, required: bool) -> int | None:
            node = root.find(tag)
            if node is None or not (node.text or "").strip():
                if required:
                    raise ValueError(f"У XML відсутнє поле <{tag}>.")
                return None
            return _b64_to_int(node.text, tag)

        n = field("Modulus", True)
        e = field("Exponent", True)
        d, p, q = field("D", False), field("P", False), field("Q", False)
        if d is not None and p is not None and q is not None:
            return build_key(p, q, e, d)
        return cls(n=n, e=e, d=d)


def build_key(p, q, e, d=None) -> RSAKey:
    """Формує пару ключів із заданих p, q, e (d = e^-1 mod φ(n))"""
    p, q, e, phi = RSAKeyValidator.validate_components(p, q, e)
    computed_d = mod_inverse(e, phi)
    n = p * q
    if d is not None and pow(pow(2, e, n), d, n) != 2:
        raise ValueError("Число d не відповідає ключам p, q, e.")
    return RSAKey(n=n, e=e, d=computed_d if d is None else d, p=p, q=q)


def generate_keypair(bits=1024, e=None, max_attempts: int = 1000) -> RSAKey:
    """Генерує випадкову пару ключів розміром `bits` біт.

    Якщо e не задано, береться 65537 (як у .NET), а для малих ключів –
    найбільше з 257, 17, 5, 3, що підходить"""
    bits = RSAKeyValidator.validate_bits(bits)
    fixed_e = None if e in (None, "") else RSAKeyValidator.validate_exponent(e)

    p_bits = bits // 2
    q_bits = bits - p_bits
    for _ in range(max_attempts):
        p, q = generate_prime(p_bits), generate_prime(q_bits)
        if p == q:
            continue
        phi = (p - 1) * (q - 1)
        candidates = (fixed_e,) if fixed_e is not None else _FALLBACK_EXPONENTS
        for candidate in candidates:
            if candidate < phi and math.gcd(candidate, phi) == 1:
                return RSAKey(n=p * q, e=candidate, d=mod_inverse(candidate, phi), p=p, q=q)
    raise ValueError(
        f"Не вдалося згенерувати ключ з e = {fixed_e} для {bits} біт. "
        "Оберіть інше e або більший розмір ключа."
    )


def parse_public_key(text) -> RSAKey:
    e, n = RSAKeyValidator.parse_pair(text, "e")
    return RSAKey(n=n, e=e)


__all__ = ["RSAKey", "build_key", "generate_keypair", "parse_public_key", "DEFAULT_PUBLIC_EXPONENT"]
