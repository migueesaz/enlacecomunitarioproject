from datetime import date
from io import BytesIO
import re

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

MESES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]

# =============================================================================
# Datos de la comunidad. Ajustar aquí los datos generales del Consejo Comunal
# que se imprimen en el membrete y en el cuerpo de las cartas.
# =============================================================================
CONFIG = {
    "consejo_comunal": "La Cruz",
    "sector": "La Cruz",
    "municipio": "Guacara",
    "parroquia": "Ciudad Alianza",
    "registro_n": "",
    "rif": "",
    "certificado": "",
    # Datos del emprendimiento para la carta aval
    "emprendimiento_nombre": "Leidy's & Princess",
    "emprendimiento_actividad": "de Confección, Diseño y Venta al mayor y detal de prendas de vestir",
    "emprendimiento_direccion": "la casa 5-2-68 ubicada en la Urbanización Aguamarina 5-2",
    "emprendimiento_desde": "2018",
    # Datos no registrados en la base de datos (dejar en blanco para llenar a mano)
    "estado_civil": "",
    "profesion": "",
}

_MARGEN = 2 * cm


def _estilos():
    return {
        "membrete": ParagraphStyle(
            "membrete",
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=14,
            alignment=TA_CENTER,
        ),
        "titulo": ParagraphStyle(
            "titulo",
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            spaceBefore=6,
            spaceAfter=14,
        ),
        "cuerpo": ParagraphStyle(
            "cuerpo",
            fontName="Helvetica",
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
        ),
        "firma": ParagraphStyle(
            "firma",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
        ),
        "firma_der": ParagraphStyle(
            "firma_der",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            alignment=TA_RIGHT,
        ),
    }


def _nuevo_documento():
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=_MARGEN,
        rightMargin=_MARGEN,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title="Carta del Consejo Comunal",
        author=CONFIG["consejo_comunal"],
    )
    return doc, buffer


def _membrete_residencia(story, estilos):
    story.append(Paragraph("REPÚBLICA BOLIVARIANA DE VENEZUELA", estilos["membrete"]))
    story.append(
        Paragraph("MINISTERIO DEL PODER POPULAR PARA LAS COMUNAS", estilos["membrete"])
    )
    story.append(Paragraph("CONSEJO COMUNAL", estilos["membrete"]))
    registro = CONFIG["registro_n"] or "_______________"
    story.append(Paragraph(f"REGISTRO N° {registro}", estilos["membrete"]))
    story.append(Spacer(1, 0.5 * cm))


def _firmas_residencia(story, estilos):
    story.append(Spacer(1, 1.6 * cm))
    ancho = letter[0] - 2 * _MARGEN
    tabla = Table(
        [
            [
                Paragraph("VOC. EJECUTIVO", estilos["firma"]),
                Paragraph("VOC. ADMIN Y FINANZAS", estilos["firma"]),
            ],
            [
                Paragraph("VOC. CONTRALORÍA SOCIAL", estilos["firma"]),
                "",
            ],
        ],
        colWidths=[ancho / 2, ancho / 2],
        hAlign="CENTER",
    )
    tabla.setStyle(
        TableStyle(
            [
                ("SPAN", (0, 1), (1, 1)),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 1), (-1, 1), 28),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(tabla)


def _cedula_v(cedula):
    cedula = str(cedula or "").strip()
    coincidencia = re.match(r"^([VvEeJjPp])\s*-?\s*(.*)$", cedula)
    if coincidencia:
        return f"{coincidencia.group(1).upper()}-{coincidencia.group(2)}"
    return f"V-{cedula}" if cedula else "_______________"


def _datos_vecino(datos):
    nombre_completo = f"{datos.get('nombre', '')} {datos.get('apellido', '')}".strip()
    return {
        "nombre_completo": nombre_completo or "________________________",
        "cedula": _cedula_v(datos.get("cedula")),
        "direccion": datos.get("direccion") or "______________________________",
    }


def generar_carta_residencia(datos_vecino, fecha=None):
    v = _datos_vecino(datos_vecino)
    fecha = fecha or date.today()
    dia = fecha.day
    mes = MESES[fecha.month - 1]
    anio = fecha.year

    doc, buffer = _nuevo_documento()
    estilos = _estilos()
    story = []

    _membrete_residencia(story, estilos)
    story.append(Paragraph("CARTA DE RESIDENCIA", estilos["titulo"]))

    cuerpo = (
        f"Por medio de la presente, el Consejo Comunal {CONFIG['consejo_comunal']}, "
        f"ubicado en el sector {CONFIG['sector']}, Municipio {CONFIG['municipio']}, "
        "previo conocimiento y autorización del Ministerio del Poder Popular para las "
        "Comunas y Protección Social; en ejercicio del poder popular."
    )
    story.append(Paragraph(cuerpo, estilos["cuerpo"]))

    cuerpo = (
        f"Hacemos constar que hoy {dia} de {mes} del {anio} compareció ante este ente "
        f"el (la) ciudadano (a) {v['nombre_completo']}, C.I: {v['cedula']}, quién "
        "habiendo sido impuesto del contenido del artículo 320 del Código Penal "
        "Venezolano referido al falso testimonio ante funcionarios públicos o en qué "
        f"tramitador, manifestó estar residenciado en {v['direccion']} del Urbanismo "
        "antes mencionado."
    )
    story.append(Paragraph(cuerpo, estilos["cuerpo"]))

    cuerpo = (
        "Cuyos efectos antes consignados documentación pertinente que así lo demuestra, "
        "en virtud de lo cual se expide la presente constancia de residencia a los fines "
        "únicos de cumplir con los requisitos señalados para trámites:"
    )
    story.append(Paragraph(cuerpo, estilos["cuerpo"]))

    cuerpo = (
        "Constancia que se expide a solicitud de la parte interesada, de conformidad con "
        "lo establecido en el artículo 11 de la Ley Orgánica de Registro Civil y con base "
        f"a la información suministrada en Caracas, a los {dia} días del mes de {mes} del "
        f"{anio}."
    )
    story.append(Paragraph(cuerpo, estilos["cuerpo"]))

    cuerpo = (
        "En concordancia con los artículos 321, 322 y 325 del Código Orgánico Penal serán "
        "sancionados aquellos que incurran en el delito de alteración del presente "
        "documento ya que el mismo es intransferible."
    )
    story.append(Paragraph(cuerpo, estilos["cuerpo"]))

    _firmas_residencia(story, estilos)

    doc.build(story)
    return buffer.getvalue()


def generar_carta_aval(datos_vecino, fecha=None):
    v = _datos_vecino(datos_vecino)
    fecha = fecha or date.today()
    dia = fecha.day
    mes = MESES[fecha.month - 1]
    anio = fecha.year

    doc, buffer = _nuevo_documento()
    estilos = _estilos()
    story = []

    story.append(Paragraph("REPÚBLICA BOLIVARIANA DE VENEZUELA", estilos["membrete"]))
    story.append(Paragraph(f"MUNICIPIO {CONFIG['municipio']}", estilos["membrete"]))
    story.append(Paragraph(f"PARROQUIA {CONFIG['parroquia']}", estilos["membrete"]))
    rif = CONFIG["rif"] or "_______________"
    certificado = CONFIG["certificado"] or "_______________"
    story.append(
        Paragraph(f"RIF.: {rif} &nbsp;&nbsp;&nbsp;&nbsp; CERTIFICADO: {certificado}", estilos["membrete"])
    )
    story.append(
        Paragraph(
            f"CONSEJO COMUNAL \"{CONFIG['consejo_comunal']}\"",
            estilos["membrete"],
        )
    )
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("CARTA AVAL", estilos["titulo"]))

    estado_civil = datos_vecino.get("estado_civil") or CONFIG["estado_civil"] or "_______________"
    profesion = datos_vecino.get("profesion") or CONFIG["profesion"] or "_______________"
    cuerpo = (
        f"Quien suscribe los integrantes del Consejo Comunal "
        f"\"{CONFIG['consejo_comunal']}\" hacemos constar que el (la) ciudadano (a): "
        f"{v['nombre_completo']}, Venezolano (a), portador de la cédula de identidad N° "
        f"{v['cedula']}, estado civil {estado_civil}, profesión u oficio {profesion}, "
        f"damos Fe del funcionamiento del Emprendimiento "
        f"{CONFIG['emprendimiento_actividad']} \"{CONFIG['emprendimiento_nombre']}\" en "
        f"{CONFIG['emprendimiento_direccion']} desde el año {CONFIG['emprendimiento_desde']} "
        "a la fecha."
    )
    story.append(Paragraph(cuerpo, estilos["cuerpo"]))

    cuerpo = (
        f"Constancia que se expide a petición de la parte interesada a los {dia} días del "
        f"mes de {mes} del año {anio}."
    )
    story.append(Paragraph(cuerpo, estilos["cuerpo"]))

    story.append(Spacer(1, 1.6 * cm))
    story.append(Paragraph("P/EL CONSEJO COMUNAL", estilos["firma_der"]))

    doc.build(story)
    return buffer.getvalue()


def generar_carta_buena_conducta(datos_vecino, fecha=None):
    v = _datos_vecino(datos_vecino)
    fecha = fecha or date.today()
    dia = fecha.day
    mes = MESES[fecha.month - 1]
    anio = fecha.year

    doc, buffer = _nuevo_documento()
    estilos = _estilos()
    story = []

    _membrete_residencia(story, estilos)
    story.append(Paragraph("CARTA DE BUENA CONDUCTA", estilos["titulo"]))

    cuerpo = (
        f"Por medio de la presente, el Consejo Comunal {CONFIG['consejo_comunal']}, "
        f"ubicado en el sector {CONFIG['sector']}, Municipio {CONFIG['municipio']}, hace "
        f"constar que el (la) ciudadano (a) {v['nombre_completo']}, titular de la cédula "
        f"de identidad N° {v['cedula']}, residente en {v['direccion']}, ha mantenido "
        "una conducta social y moral acorde con los principios de sana convivencia "
        "comunitaria durante el tiempo de residencia en la comunidad, sin que se le hayan "
        "registrado hechos que atenten contra el orden público y el bienestar colectivo."
    )
    story.append(Paragraph(cuerpo, estilos["cuerpo"]))

    cuerpo = (
        f"Constancia que se expide a petición de la parte interesada, a los {dia} días del "
        f"mes de {mes} del año {anio}."
    )
    story.append(Paragraph(cuerpo, estilos["cuerpo"]))

    _firmas_residencia(story, estilos)

    doc.build(story)
    return buffer.getvalue()


def generar_carta(tipo_carta, datos_vecino, fecha=None):
    tipo = (tipo_carta or "").strip().lower()
    if "aval" in tipo:
        return generar_carta_aval(datos_vecino, fecha)
    if "conducta" in tipo:
        return generar_carta_buena_conducta(datos_vecino, fecha)
    if "residencia" in tipo or "constancia" in tipo:
        return generar_carta_residencia(datos_vecino, fecha)
    raise ValueError(f"Tipo de carta no soportado: {tipo_carta}")


def nombre_archivo(tipo_carta, datos_vecino):
    tipo = (tipo_carta or "carta").strip().lower().replace(" ", "_")
    cedula = str(datos_vecino.get("cedula") or "desconocido")
    return f"carta_{tipo}_{cedula}.pdf"
