from typing import Any


def build_gesetz_vorgang_data(
    *, base_vorgang_data: dict[str, Any], dok_datas: list[dict[str, Any]], neben_eintrag_data: list[dict[str, Any]]
) -> dict[str, Any]:
    """Builds a dict for GesetzVorgang BaseModel instantiation."""
    return {**base_vorgang_data, "Dokument": dok_datas, "Nebeneintrag": neben_eintrag_data}
