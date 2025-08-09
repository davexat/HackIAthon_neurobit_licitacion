import csv
from pathlib import Path

def ensure_dir(file_path):
    OUTPUT_DIR = Path("data/training.csv")
    OUTPUT_DIR.parent.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR

def generate_training_data():
    OUTPUT_FILE = ensure_dir("data/training.csv")

    data = [
    # --- Condiciones Legales ---
    ("El contratista deberá cumplir con todas las leyes laborales vigentes.", "Condiciones Legales"),
    ("El oferente acepta las condiciones establecidas en el presente contrato.", "Condiciones Legales"),
    ("Se prohíbe la subcontratación sin autorización previa de la entidad contratante.", "Condiciones Legales"),
    ("El contrato será firmado en presencia de un notario público.", "Condiciones Legales"),
    ("La empresa adjudicataria deberá presentar póliza de responsabilidad civil.", "Condiciones Legales"),
    ("Las controversias se resolverán mediante arbitraje en la Cámara de Comercio.", "Condiciones Legales"),
    ("El incumplimiento de cláusulas resultará en la rescisión del contrato.", "Condiciones Legales"),
    ("Se requerirá certificado de no tener impedimento legal para contratar.", "Condiciones Legales"),
    ("La garantía de cumplimiento tendrá una vigencia mínima de doce meses.", "Condiciones Legales"),
    ("El proveedor acepta que la ley aplicable será la ecuatoriana.", "Condiciones Legales"),
    ("Los pagos se realizarán únicamente si se cumplen todas las disposiciones contractuales.", "Condiciones Legales"),
    ("El contrato entrará en vigor a partir de la fecha de su firma.", "Condiciones Legales"),
    ("No se permitirá la cesión de derechos sin consentimiento por escrito.", "Condiciones Legales"),

    # --- Condiciones Técnicas ---
    ("El plazo de ejecución de la obra será de 90 días calendario.", "Condiciones Técnicas"),
    ("Se deberá utilizar cemento tipo I con resistencia mínima de 4000 psi.", "Condiciones Técnicas"),
    ("El oferente deberá garantizar que el personal cuente con certificaciones de seguridad.", "Condiciones Técnicas"),
    ("Se deberá realizar inspección diaria de la obra por parte del supervisor.", "Condiciones Técnicas"),
    ("Todos los equipos deberán cumplir con las normas ISO 9001.", "Condiciones Técnicas"),
    ("El cableado deberá ser de cobre y cumplir con norma NTE INEN.", "Condiciones Técnicas"),
    ("Se instalarán luminarias LED de alta eficiencia en todas las áreas.", "Condiciones Técnicas"),
    ("La obra deberá incluir accesos para personas con discapacidad.", "Condiciones Técnicas"),
    ("Los planos estructurales deberán estar firmados por un ingeniero civil colegiado.", "Condiciones Técnicas"),
    ("El hormigón deberá cumplir con resistencia especificada en ficha técnica.", "Condiciones Técnicas"),
    ("Se deberán tomar medidas de mitigación de polvo durante la construcción.", "Condiciones Técnicas"),
    ("La impermeabilización será aplicada en todas las cubiertas.", "Condiciones Técnicas"),
    ("El pintado final se realizará con pintura ecológica base agua.", "Condiciones Técnicas"),

    # --- Condiciones Económicas ---
    ("El monto total de la oferta es de $450,000 dólares americanos.", "Condiciones Económicas"),
    ("El anticipo solicitado será del 30% del valor total del contrato.", "Condiciones Económicas"),
    ("El oferente deberá presentar desglose detallado de costos unitarios.", "Condiciones Económicas"),
    ("Los precios ofertados incluyen transporte y seguro hasta el lugar de entrega.", "Condiciones Económicas"),
    ("El pago se realizará en tres cuotas iguales contra avance de obra.", "Condiciones Económicas"),
    ("Se aplicará una multa de 0.5% por cada día de retraso.", "Condiciones Económicas"),
    ("El presupuesto estimado asciende a $1,200,000.", "Condiciones Económicas"),
    ("Los valores están expresados en dólares estadounidenses y no incluyen IVA.", "Condiciones Económicas"),
    ("Se aceptará pago mediante transferencia bancaria a cuenta registrada.", "Condiciones Económicas"),
    ("El oferente deberá incluir todos los impuestos en su propuesta.", "Condiciones Económicas"),
    ("El ajuste de precios se aplicará cada seis meses según índice oficial.", "Condiciones Económicas"),
    ("No se reconocerán gastos adicionales no contemplados en la oferta inicial.", "Condiciones Económicas"),
    ("El costo por metro cuadrado ofertado es de $350.", "Condiciones Económicas"),
    ]

    with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "category"])  # Cabeceras
        writer.writerows(data)