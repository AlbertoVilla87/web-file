import re


class Politics:

    NAME = "name"
    REGEX = "regex"

    INTER_REGEX = re.compile(
        r"(\bEl señor\b|\bLa señora\b|\bEl señora\b)([ \wÁÉÍÓÚ+-?]+)(\(.*\))?:"
    )

    REGEX = {
        "Sánchez Pérez-Castejón, Pedro": [
            re.compile(
                r"(\bEl señor\b|\bLa señora\b|\bEl señora\b)( PRESIDENTE DEL GOBIERNO\s*)(\(.*\))?:"
            ),
            re.compile(
                r"(\bEl señor\b|\bLa señora\b|\bEl señora\b)( SÁNCHEZ PÉREZ-CASTEJÓN\s*)(\(.*\))?:"
            ),
        ],
        "Díaz Pérez, Yolanda": [
            re.compile(
                r"(\bLa señora\b)( VICEPRESIDENTA SEGUNDA Y MINISTRA DE TRABAJO Y ECONOMÍA SOCIAL\s*)(\(.*\))?:"
            ),
            re.compile(
                r"(\bLa señora\b)( VICEPRESIDENTA SEGUNDA Y MINISTRA DE TRABAJO Y ECOCONOMÍA SOCIAL\s*)(\(.*\))?:"
            ),
            re.compile(
                r"(\bLa señora\b)( VICEPRESIDENTA SEGUNDA DEL GOBIERNO Y MINISTRA DE TRABAJO Y ECONOMÍA SOCIAL\s*)(\(.*\))?:"
            ),
            re.compile(
                r"(\bLa señora\b)( VICEPRESIDENTA TERCERA DEL GOBIERNO Y MINISTRA DE TRABAJO Y ECONOMÍA SOCIAL\s*)(\(.*\))?:"
            ),
            re.compile(
                r"(\bLa señora\b)( VICEPRESIDENTA TERCERA Y MINISTRA DE TRABAJO Y ECONOMÍA SOCIAL\s*)(\(.*\))?:"
            ),
            re.compile(
                r"(\bLa señora\b)( MINISTRA DE TRABAJO Y ECONOMÍA SOCIAL\s*)(\(.*\))?:"
            ),
        ],
        "Abascal Conde, Santiago": [
            re.compile(r"(\bEl señor\b)( ABASCAL CONDE\s*)(\(.*\))?:"),
            re.compile(
                r"(\bEl señor\b)( CANDIDATO A LA PRESIDENCIA DEL GOBIERNO \(Abascal Conde\)\s*)(\(.*\))?:"
            ),
        ],
    }

    NAMES = REGEX.keys()
