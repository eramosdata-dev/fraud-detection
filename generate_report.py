from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    HRFlowable,
)
from reportlab.lib.enums import TA_CENTER
from pathlib import Path

# ── Rutas ─────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
FIG_DIR = BASE_DIR / "reports" / "figures"
OUT_PDF = BASE_DIR / "reports" / "Fraud_Detection_Report.pdf"
OUT_PDF.parent.mkdir(parents=True, exist_ok=True)

# ── Documento ─────────────────────────────────────────────────
doc = SimpleDocTemplate(
    str(OUT_PDF),
    pagesize=A4,
    rightMargin=2 * cm,
    leftMargin=2 * cm,
    topMargin=2 * cm,
    bottomMargin=2 * cm,
)

# ── Estilos de texto ──────────────────────────────────────────
estilo_titulo = ParagraphStyle(
    "titulo",
    fontSize=24,
    leading=30,
    fontName="Helvetica-Bold",
    textColor=colors.HexColor("#1A237E"),
    alignment=TA_CENTER,
    spaceAfter=8,
)
estilo_subtitulo = ParagraphStyle(
    "subtitulo",
    fontSize=13,
    leading=16,
    fontName="Helvetica",
    textColor=colors.HexColor("#424242"),
    alignment=TA_CENTER,
    spaceAfter=20,
)
estilo_seccion = ParagraphStyle(
    "seccion",
    fontSize=14,
    fontName="Helvetica-Bold",
    textColor=colors.HexColor("#1565C0"),
    spaceBefore=16,
    spaceAfter=8,
)
estilo_texto = ParagraphStyle(
    "texto",
    fontSize=10,
    fontName="Helvetica",
    textColor=colors.HexColor("#212121"),
    spaceAfter=6,
    leading=16,
)
estilo_caption = ParagraphStyle(
    "caption",
    fontSize=9,
    fontName="Helvetica-Oblique",
    textColor=colors.HexColor("#757575"),
    alignment=TA_CENTER,
    spaceAfter=12,
)

# ── Helpers ───────────────────────────────────────────────────
estilo_tabla = TableStyle(
    [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565C0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        (
            "ROWBACKGROUNDS",
            (0, 1),
            (-1, -1),
            [colors.HexColor("#F5F5F5"), colors.white],
        ),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]
)


def agregar_tabla(datos, anchos):
    t = Table(datos, colWidths=[a * cm for a in anchos])
    t.setStyle(estilo_tabla)
    contenido.append(t)
    contenido.append(Spacer(1, 0.3 * cm))


def agregar_figura(nombre, ancho, alto, pie):
    ruta = FIG_DIR / nombre
    if ruta.exists():
        contenido.append(Image(str(ruta), width=ancho * cm, height=alto * cm))
        contenido.append(Paragraph(pie, estilo_caption))
    else:
        print(f"AVISO: falta la figura {nombre}")


# ── Contenido ─────────────────────────────────────────────────
contenido = []

# ── Título ────────────────────────────────────────────────────
contenido.append(Spacer(1, 1 * cm))
contenido.append(Paragraph("Fraud Detection", estilo_titulo))
contenido.append(
    Paragraph("Detección de fraude en transacciones con tarjeta", estilo_subtitulo)
)
contenido.append(
    HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1565C0"))
)
contenido.append(Spacer(1, 0.5 * cm))

# ── 1. Contexto ───────────────────────────────────────────────
contenido.append(Paragraph("1. Contexto de Negocio", estilo_seccion))
contenido.append(
    Paragraph(
        "El objetivo es detectar transacciones fraudulentas con tarjeta de crédito. "
        "Solo 492 de 284,807 operaciones son fraude (0.1727%, ratio 1:577), por lo "
        "que la exactitud (accuracy) no sirve como métrica: un modelo que siempre "
        "dijera 'legítima' acertaría el 99.83% sin detectar ningún fraude. Se usa "
        "AUC-PR, precision y recall.",
        estilo_texto,
    )
)

# ── 2. Dataset ────────────────────────────────────────────────
contenido.append(Paragraph("2. Dataset", estilo_seccion))
agregar_tabla(
    [
        ["Campo", "Valor"],
        ["Fuente", "Credit Card Fraud Detection — Kaggle"],
        ["Registros", "284,807 transacciones (48 horas)"],
        ["Variables", "Time, Amount, V1-V28 (PCA) y Class"],
        ["Fraudes", "492 (0.1727%)"],
        ["Ratio desbalanceo", "1:577"],
    ],
    [7, 9],
)

# ── 3. Hallazgos EDA ──────────────────────────────────────────
contenido.append(Paragraph("3. Hallazgos del Análisis Exploratorio", estilo_seccion))
contenido.append(
    Paragraph(
        "Los fraudes se concentran de madrugada: a las 2h la tasa llega al 1.71%. "
        "Además suelen ser de importe pequeño: la mediana es de 9.25 € frente a "
        "22.00 € en las legítimas, coherente con el testeo de tarjetas robadas. "
        "Los componentes V4, V14, V3 y V17 son los que mejor separan las clases.",
        estilo_texto,
    )
)
agregar_figura(
    "02_analisis_temporal.png",
    15,
    8.5,
    "Figura 1 — Volumen y tasa de fraude por hora del día",
)
agregar_figura(
    "03_analisis_montos.png",
    15,
    5.5,
    "Figura 2 — Distribución de montos: legítimas frente a fraudes",
)

# ── 4. Metodología ────────────────────────────────────────────
contenido.append(Paragraph("4. Metodología del Modelo", estilo_seccion))
contenido.append(
    Paragraph(
        "Se aplicó SMOTE solo sobre el conjunto de entrenamiento (fraudes al 10%) "
        "y se compararon LightGBM y XGBoost. La evaluación se hizo sobre un test "
        "sin modificar (20%, con 98 fraudes) y el umbral de decisión se optimizó "
        "en lugar de usar 0.5.",
        estilo_texto,
    )
)
agregar_tabla(
    [
        ["Etapa", "Técnica", "Herramienta"],
        ["Desbalanceo", "SMOTE (solo en train)", "imbalanced-learn"],
        ["Modelos", "LightGBM y XGBoost", "lightgbm, xgboost"],
        ["Métrica principal", "AUC-PR", "scikit-learn"],
        ["Umbral", "Optimizado por F1 (0.9747)", "scikit-learn"],
        ["Explicabilidad", "SHAP", "shap"],
    ],
    [4.5, 6.5, 5],
)

# ── 5. Resultados ─────────────────────────────────────────────
contenido.append(Paragraph("5. Resultados del Modelo", estilo_seccion))
agregar_tabla(
    [
        ["Métrica (umbral 0.5)", "XGBoost", "LightGBM"],
        ["AUC-PR", "0.8538", "0.8659"],
        ["AUC-ROC", "0.9854", "0.9795"],
        ["F1-Score", "0.4656", "0.7311"],
    ],
    [7, 4.5, 4.5],
)
contenido.append(
    Paragraph(
        "Se eligió LightGBM por ganar en AUC-PR y en F1. Con el umbral optimizado "
        "(0.9747), el modelo final detecta 80 de 98 fraudes con 4 falsas alarmas.",
        estilo_texto,
    )
)
agregar_tabla(
    [
        ["Modelo final: LightGBM", "Valor"],
        ["Precision", "0.9524"],
        ["Recall", "0.8163"],
        ["F1-Score", "0.8791"],
    ],
    [8, 8],
)
agregar_figura(
    "07_comparacion_modelos.png", 15, 6, "Figura 3 — Curvas Precision-Recall y ROC"
)

# ── 6. Impacto y explicabilidad ───────────────────────────────
contenido.append(Paragraph("6. Impacto Económico y Explicabilidad", estilo_seccion))
agregar_tabla(
    [
        ["Concepto (test set)", "Valor"],
        ["Fraude detectado", "7,901.31 €"],
        ["Fraude no detectado", "2,746.62 €"],
        ["Valor protegido", "74.2%"],
    ],
    [8, 8],
)
agregar_figura(
    "08_confusion_matrix.png", 9, 6.4, "Figura 4 — Matriz de confusión (umbral 0.975)"
)
agregar_figura(
    "09_shap_importancia.png", 11, 8.5, "Figura 5 — Importancia de variables según SHAP"
)

# ── 7. Conclusiones ───────────────────────────────────────────
contenido.append(Paragraph("7. Conclusiones", estilo_seccion))
contenido.append(
    Paragraph(
        "LightGBM con SMOTE detecta el 82% de los fraudes del test con una "
        "precision del 95%, es decir, casi todas las alertas son fraudes reales. "
        "V4 y V14 son las variables que más influyen en las decisiones del modelo, "
        "y la hora de la transacción también aporta señal.",
        estilo_texto,
    )
)

# ── 8. Limitaciones ───────────────────────────────────────────
contenido.append(Paragraph("8. Limitaciones", estilo_seccion))
contenido.append(
    Paragraph(
        "&bull; El umbral se eligió sobre el mismo test que se usó para evaluar, "
        "por lo que las métricas finales son algo optimistas. Lo correcto sería "
        "usar un conjunto de validación aparte.",
        estilo_texto,
    )
)
contenido.append(
    Paragraph(
        "&bull; El test solo contiene 98 fraudes, así que el recall tiene un "
        "margen de error amplio: un fraude más o menos cambia varios puntos.",
        estilo_texto,
    )
)
contenido.append(
    Paragraph(
        "&bull; Los datos son de 2013 y las variables V1-V28 son anónimas, por lo "
        "que no se pueden interpretar en términos de negocio.",
        estilo_texto,
    )
)

# ── 9. Stack ──────────────────────────────────────────────────
contenido.append(Paragraph("9. Stack Tecnológico", estilo_seccion))
agregar_tabla(
    [
        ["Herramienta", "Uso"],
        ["Python 3.10", "Lenguaje principal"],
        ["Pandas / NumPy", "Manipulación de datos"],
        ["DuckDB", "SQL analítico en local"],
        ["LightGBM / XGBoost", "Modelos de clasificación"],
        ["imbalanced-learn", "SMOTE"],
        ["SHAP", "Explicabilidad"],
        ["Power BI", "Dashboard ejecutivo"],
    ],
    [6, 10],
)

# Generar PDF
doc.build(contenido)
print(f"PDF generado → {OUT_PDF.resolve()}")
