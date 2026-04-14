"""
Script de evaluación del chatbot médico
Proyecto: Chatbot médico basado en SLM para comunidades con recursos limitados
Repositorio: https://github.com/Checo194/chatbot_medico_app

Uso:
    python evaluar_chatbot.py

Sin dependencias externas — solo Python estándar.
"""

import json
import random
import math
from collections import Counter

# ─── CASOS DE PRUEBA (60 casos simulados) ─────────────────────────────────────

CASOS = [
    # Categoría 1: Infecciones respiratorias leves (15 casos)
    {"id": "R01", "categoria": "respiratorio",
     "sintomas": "tos seca, fiebre leve 37.5, malestar general desde hace 2 días",
     "respuesta_referencia": "Probable infección respiratoria viral. Reposo, hidratación y paracetamol. No requiere antibiótico. Monitorear si fiebre supera 39°C.",
     "nivel_atencion": "primer_nivel"},
    {"id": "R02", "categoria": "respiratorio",
     "sintomas": "dolor de garganta, dificultad para tragar, fiebre 38.5",
     "respuesta_referencia": "Posible faringoamigdalitis. Evaluar exudado. Si hay placas blancas considerar estreptococo. Paracetamol y valorar antibiótico.",
     "nivel_atencion": "primer_nivel"},
    {"id": "R03", "categoria": "respiratorio",
     "sintomas": "tos con flema amarilla, fiebre 38, dolor en pecho al respirar",
     "respuesta_referencia": "Posible bronquitis bacteriana o neumonía incipiente. Requiere auscultación. Considerar referencia para radiografía.",
     "nivel_atencion": "referencia"},
    {"id": "R04", "categoria": "respiratorio",
     "sintomas": "congestión nasal, estornudos, ojos llorosos, sin fiebre",
     "respuesta_referencia": "Rinitis alérgica o resfriado común. Antihistamínico y descongestionante. No requiere antibiótico.",
     "nivel_atencion": "primer_nivel"},
    {"id": "R05", "categoria": "respiratorio",
     "sintomas": "dificultad para respirar severa, labios morados, fiebre alta 40",
     "respuesta_referencia": "SIGNOS DE ALARMA: dificultad respiratoria severa y cianosis. Referencia urgente a segundo nivel.",
     "nivel_atencion": "urgencia"},
    {"id": "R06", "categoria": "respiratorio",
     "sintomas": "tos leve, sin fiebre, secreción nasal clara, 3 días de evolución",
     "respuesta_referencia": "Resfriado común. Manejo sintomático. Hidratación. Evolución esperada 7-10 días.",
     "nivel_atencion": "primer_nivel"},
    {"id": "R07", "categoria": "respiratorio",
     "sintomas": "tos productiva, fiebre 37.8, cansancio, dolor muscular",
     "respuesta_referencia": "Cuadro gripal. Manejo sintomático, reposo y vigilancia. Reevaluar si persiste más de 7 días.",
     "nivel_atencion": "primer_nivel"},
    {"id": "R08", "categoria": "respiratorio",
     "sintomas": "tos nocturna, sibilancias al respirar, antecedente de asma",
     "respuesta_referencia": "Crisis asmática leve. Broncodilatador de rescate. Si no mejora en 20 minutos referir a urgencias.",
     "nivel_atencion": "referencia"},
    {"id": "R09", "categoria": "respiratorio",
     "sintomas": "ronquera, tos seca, sin fiebre, 5 días",
     "respuesta_referencia": "Laringitis viral. Reposo vocal y analgésico. Resolución espontánea en 1-2 semanas.",
     "nivel_atencion": "primer_nivel"},
    {"id": "R10", "categoria": "respiratorio",
     "sintomas": "fiebre 39.5, tos, dificultad respiratoria moderada, saturación 92%",
     "respuesta_referencia": "Saturación baja con fiebre alta. Referencia urgente. Posible neumonía.",
     "nivel_atencion": "urgencia"},
    {"id": "R11", "categoria": "respiratorio",
     "sintomas": "dolor facial, congestión nasal, fiebre baja, 10 días de evolución",
     "respuesta_referencia": "Posible sinusitis bacteriana. Considerar amoxicilina. Descongestionante nasal.",
     "nivel_atencion": "primer_nivel"},
    {"id": "R12", "categoria": "respiratorio",
     "sintomas": "tos, fiebre, dolor de cabeza, niño de 4 años",
     "respuesta_referencia": "Infección respiratoria en niño. Paracetamol según peso. Vigilar dificultad respiratoria.",
     "nivel_atencion": "primer_nivel"},
    {"id": "R13", "categoria": "respiratorio",
     "sintomas": "expectoración con sangre, tos crónica de 3 semanas, pérdida de peso",
     "respuesta_referencia": "ALERTA: hemoptisis y síntomas constitucionales. Descartar tuberculosis. Referencia urgente.",
     "nivel_atencion": "urgencia"},
    {"id": "R14", "categoria": "respiratorio",
     "sintomas": "tos irritativa, ambiente con mucho polvo, sin fiebre",
     "respuesta_referencia": "Tos por irritación ambiental. Evitar exposición al irritante.",
     "nivel_atencion": "primer_nivel"},
    {"id": "R15", "categoria": "respiratorio",
     "sintomas": "fiebre 38, dolor de oído, tos, niño de 2 años",
     "respuesta_referencia": "Probable otitis media en niño. Analgésico y evaluar antibiótico.",
     "nivel_atencion": "primer_nivel"},
    # Categoría 2: Gastrointestinal no complicado (15 casos)
    {"id": "G01", "categoria": "gastrointestinal",
     "sintomas": "diarrea líquida 4 veces al día, sin sangre, náuseas leves, sin fiebre",
     "respuesta_referencia": "Gastroenteritis viral. Sales de rehidratación oral, dieta blanda. Vigilar deshidratación.",
     "nivel_atencion": "primer_nivel"},
    {"id": "G02", "categoria": "gastrointestinal",
     "sintomas": "vómito y diarrea, fiebre 38, dolor abdominal tipo cólico",
     "respuesta_referencia": "Gastroenteritis aguda. Rehidratación oral prioritaria. Antiespasmódico para el cólico.",
     "nivel_atencion": "primer_nivel"},
    {"id": "G03", "categoria": "gastrointestinal",
     "sintomas": "diarrea con sangre, fiebre alta, dolor abdominal intenso",
     "respuesta_referencia": "ALERTA: diarrea disentérica. Referencia para cultivo y antibiótico específico.",
     "nivel_atencion": "referencia"},
    {"id": "G04", "categoria": "gastrointestinal",
     "sintomas": "acidez, dolor en boca del estómago, peor después de comer",
     "respuesta_referencia": "Gastritis o reflujo. Antiácido o inhibidor de bomba de protones. Dieta sin irritantes.",
     "nivel_atencion": "primer_nivel"},
    {"id": "G05", "categoria": "gastrointestinal",
     "sintomas": "estreñimiento, 5 días sin evacuación, dolor abdominal leve",
     "respuesta_referencia": "Estreñimiento funcional. Laxante osmótico, aumentar fibra e hidratación.",
     "nivel_atencion": "primer_nivel"},
    {"id": "G06", "categoria": "gastrointestinal",
     "sintomas": "dolor abdominal intenso en fosa ilíaca derecha, náuseas, fiebre",
     "respuesta_referencia": "ALERTA: posible apendicitis. Referencia urgente a cirugía.",
     "nivel_atencion": "urgencia"},
    {"id": "G07", "categoria": "gastrointestinal",
     "sintomas": "náuseas matutinas, vómito leve, embarazo de 8 semanas",
     "respuesta_referencia": "Náuseas del embarazo primer trimestre. Comidas pequeñas, metoclopramida si necesario.",
     "nivel_atencion": "primer_nivel"},
    {"id": "G08", "categoria": "gastrointestinal",
     "sintomas": "diarrea crónica de 3 semanas, pérdida de peso, sin fiebre",
     "respuesta_referencia": "Diarrea crónica con pérdida de peso. Descartar parasitosis. Referencia para estudios.",
     "nivel_atencion": "referencia"},
    {"id": "G09", "categoria": "gastrointestinal",
     "sintomas": "heces negras, mareo, debilidad",
     "respuesta_referencia": "ALERTA: melena. Posible sangrado gastrointestinal alto. Referencia urgente.",
     "nivel_atencion": "urgencia"},
    {"id": "G10", "categoria": "gastrointestinal",
     "sintomas": "dolor en epigastrio, ardor, mejora con antiácidos",
     "respuesta_referencia": "Compatible con gastritis o úlcera péptica. Omeprazol por 4 semanas.",
     "nivel_atencion": "primer_nivel"},
    {"id": "G11", "categoria": "gastrointestinal",
     "sintomas": "flatulencia excesiva, distensión abdominal, cambio en hábito intestinal",
     "respuesta_referencia": "Síndrome de intestino irritable. Dieta baja en FODMAP, probióticos.",
     "nivel_atencion": "primer_nivel"},
    {"id": "G12", "categoria": "gastrointestinal",
     "sintomas": "ictericia, orina oscura, dolor en hipocondrio derecho, fiebre",
     "respuesta_referencia": "ALERTA: ictericia con fiebre. Posible colecistitis. Referencia urgente.",
     "nivel_atencion": "urgencia"},
    {"id": "G13", "categoria": "gastrointestinal",
     "sintomas": "vómito repetido en niño de 1 año, sin diarrea, irritable",
     "respuesta_referencia": "Vómito en lactante. Evaluar deshidratación. Rehidratación oral fraccionada.",
     "nivel_atencion": "primer_nivel"},
    {"id": "G14", "categoria": "gastrointestinal",
     "sintomas": "diarrea leve post-antibiótico, sin fiebre, sin sangre",
     "respuesta_referencia": "Diarrea asociada a antibiótico. Probióticos, dieta blanda.",
     "nivel_atencion": "primer_nivel"},
    {"id": "G15", "categoria": "gastrointestinal",
     "sintomas": "dolor abdominal difuso, fiebre alta, abdomen rígido",
     "respuesta_referencia": "ALERTA: abdomen agudo con rigidez. Posible peritonitis. Referencia urgente.",
     "nivel_atencion": "urgencia"},
    # Categoría 3: Enfermedades crónicas estables (15 casos)
    {"id": "C01", "categoria": "cronico",
     "sintomas": "diabético tipo 2, glucosa en ayuno 145, sin síntomas agudos, control rutinario",
     "respuesta_referencia": "Control glucémico mejorable. Reforzar dieta y actividad física. Mantener metformina. Control en 3 meses.",
     "nivel_atencion": "primer_nivel"},
    {"id": "C02", "categoria": "cronico",
     "sintomas": "hipertenso, presión 160/100, cefalea leve, toma su medicamento",
     "respuesta_referencia": "Hipertensión mal controlada. Ajustar dosis antihipertensivo. Reducir sal. Control en 2 semanas.",
     "nivel_atencion": "primer_nivel"},
    {"id": "C03", "categoria": "cronico",
     "sintomas": "diabético, glucosa 380, vómito, confusión, deshidratación",
     "respuesta_referencia": "ALERTA: crisis hiperglucémica. Posible cetoacidosis. Referencia urgente para insulina IV.",
     "nivel_atencion": "urgencia"},
    {"id": "C04", "categoria": "cronico",
     "sintomas": "hipertenso, presión 200/120, dolor de cabeza intenso, visión borrosa",
     "respuesta_referencia": "ALERTA: crisis hipertensiva. Riesgo cerebrovascular. Referencia urgente.",
     "nivel_atencion": "urgencia"},
    {"id": "C05", "categoria": "cronico",
     "sintomas": "paciente con hipotiroidismo, cansancio, aumento de peso, toma levotiroxina",
     "respuesta_referencia": "Hipotiroidismo en tratamiento. Verificar adherencia. Solicitar TSH para ajuste de dosis.",
     "nivel_atencion": "primer_nivel"},
    {"id": "C06", "categoria": "cronico",
     "sintomas": "asmático, usa inhalador 3 veces al día, despertares nocturnos frecuentes",
     "respuesta_referencia": "Asma mal controlada. Revisar técnica inhalatoria. Considerar corticoide inhalado. Referencia.",
     "nivel_atencion": "referencia"},
    {"id": "C07", "categoria": "cronico",
     "sintomas": "diabético, úlcera en pie que no cicatriza, sin dolor por neuropatía",
     "respuesta_referencia": "Pie diabético. Herida de alto riesgo. Referencia urgente a segundo nivel.",
     "nivel_atencion": "urgencia"},
    {"id": "C08", "categoria": "cronico",
     "sintomas": "hipertenso controlado, presión 125/80, sin molestias, control semestral",
     "respuesta_referencia": "Hipertensión bien controlada. Continuar tratamiento. Control en 6 meses.",
     "nivel_atencion": "primer_nivel"},
    {"id": "C09", "categoria": "cronico",
     "sintomas": "adulto mayor con artritis, dolor en rodillas, sin cambios agudos",
     "respuesta_referencia": "Osteoartritis estable. Paracetamol para el dolor. Fisioterapia.",
     "nivel_atencion": "primer_nivel"},
    {"id": "C10", "categoria": "cronico",
     "sintomas": "epiléptico controlado, sin crisis en 6 meses, toma valproato",
     "respuesta_referencia": "Epilepsia bien controlada. Mantener medicación. Control neurológico anual.",
     "nivel_atencion": "primer_nivel"},
    {"id": "C11", "categoria": "cronico",
     "sintomas": "diabético, hormigueo y entumecimiento en pies, glucosa bien controlada",
     "respuesta_referencia": "Neuropatía diabética. Optimizar glucemia. Considerar pregabalina para el dolor.",
     "nivel_atencion": "primer_nivel"},
    {"id": "C12", "categoria": "cronico",
     "sintomas": "hipertenso, con edema en piernas, disnea al caminar, tos nocturna",
     "respuesta_referencia": "ALERTA: posible insuficiencia cardíaca. Referencia urgente para evaluación cardiológica.",
     "nivel_atencion": "urgencia"},
    {"id": "C13", "categoria": "cronico",
     "sintomas": "paciente con EPOC, más tos y flema que de costumbre, fiebre leve",
     "respuesta_referencia": "Exacerbación leve de EPOC. Antibiótico y broncodilatador. Si no mejora en 48h referir.",
     "nivel_atencion": "primer_nivel"},
    {"id": "C14", "categoria": "cronico",
     "sintomas": "adulto mayor hipertenso, caída al levantarse, mareo ortostático",
     "respuesta_referencia": "Hipotensión ortostática. Revisar dosis antihipertensivo. Medidas de seguridad para caídas.",
     "nivel_atencion": "primer_nivel"},
    {"id": "C15", "categoria": "cronico",
     "sintomas": "diabético sin control, no toma medicamento desde hace 2 meses, glucosa 290",
     "respuesta_referencia": "Descontrol glucémico. Reiniciar metformina. Educación sobre adherencia. Control en 2 semanas.",
     "nivel_atencion": "primer_nivel"},
    # Categoría 4: Orientación preventiva (15 casos)
    {"id": "P01", "categoria": "preventivo",
     "sintomas": "mujer de 45 años sin síntomas, solicita chequeo general",
     "respuesta_referencia": "Consulta preventiva. Solicitar glucosa, colesterol, presión arterial, Papanicolaou.",
     "nivel_atencion": "primer_nivel"},
    {"id": "P02", "categoria": "preventivo",
     "sintomas": "niño de 2 años, consulta para vacunación, sano",
     "respuesta_referencia": "Verificar esquema de vacunación. Aplicar vacunas de los 2 años.",
     "nivel_atencion": "primer_nivel"},
    {"id": "P03", "categoria": "preventivo",
     "sintomas": "embarazo de 12 semanas, primera consulta prenatal, sin molestias",
     "respuesta_referencia": "Primera consulta prenatal. Exámenes básicos, ácido fólico, señales de alarma.",
     "nivel_atencion": "primer_nivel"},
    {"id": "P04", "categoria": "preventivo",
     "sintomas": "hombre de 50 años, fumador, sin síntomas, quiere chequeo",
     "respuesta_referencia": "Prevención en fumador. Glucosa, presión, perfil lipídico. Consejería para dejar de fumar.",
     "nivel_atencion": "primer_nivel"},
    {"id": "P05", "categoria": "preventivo",
     "sintomas": "adolescente de 14 años, consulta por planificación familiar",
     "respuesta_referencia": "Salud reproductiva adolescente. Orientación sin juicio sobre métodos anticonceptivos.",
     "nivel_atencion": "primer_nivel"},
    {"id": "P06", "categoria": "preventivo",
     "sintomas": "adulto mayor de 70 años, solo, consulta general, sin síntomas",
     "respuesta_referencia": "Valoración geriátrica. Evaluar funcionalidad, caídas, medicamentos. Vacunas.",
     "nivel_atencion": "primer_nivel"},
    {"id": "P07", "categoria": "preventivo",
     "sintomas": "trabajador agrícola, exposición a agroquímicos, sin síntomas actuales",
     "respuesta_referencia": "Salud ocupacional. Orientar sobre equipo de protección. Vigilar síntomas neurológicos.",
     "nivel_atencion": "primer_nivel"},
    {"id": "P08", "categoria": "preventivo",
     "sintomas": "familia con agua de pozo, varios miembros con diarrea recurrente",
     "respuesta_referencia": "Posible contaminación del agua. Orientar sobre cloración y lavado de manos.",
     "nivel_atencion": "primer_nivel"},
    {"id": "P09", "categoria": "preventivo",
     "sintomas": "mujer de 35 años, antecedente familiar de diabetes, sin síntomas",
     "respuesta_referencia": "Prevención de diabetes. Glucosa anual, IMC, dieta saludable y actividad física.",
     "nivel_atencion": "primer_nivel"},
    {"id": "P10", "categoria": "preventivo",
     "sintomas": "niño de 5 años, bajo peso para su edad, come poco",
     "respuesta_referencia": "Riesgo de desnutrición. Evaluación nutricional, curva de crecimiento. Consejería alimentaria.",
     "nivel_atencion": "primer_nivel"},
    {"id": "P11", "categoria": "preventivo",
     "sintomas": "recién nacido de 3 días, primera consulta, lactancia materna",
     "respuesta_referencia": "Control del recién nacido. Verificar ictericia y peso. Orientar lactancia exclusiva.",
     "nivel_atencion": "primer_nivel"},
    {"id": "P12", "categoria": "preventivo",
     "sintomas": "adulto con antecedente de tuberculosis hace 5 años, sano actualmente",
     "respuesta_referencia": "Seguimiento post-tuberculosis. Vigilar síntomas de reactivación. Nutrición e higiene.",
     "nivel_atencion": "primer_nivel"},
    {"id": "P13", "categoria": "preventivo",
     "sintomas": "comunidad con casos de dengue reportados, consulta por prevención",
     "respuesta_referencia": "Prevención de dengue. Eliminar criaderos, repelente, manga larga.",
     "nivel_atencion": "primer_nivel"},
    {"id": "P14", "categoria": "preventivo",
     "sintomas": "mujer embarazada de 36 semanas, sana, control prenatal",
     "respuesta_referencia": "Control prenatal tercer trimestre. Verificar posición fetal, presión, plan de parto.",
     "nivel_atencion": "primer_nivel"},
    {"id": "P15", "categoria": "preventivo",
     "sintomas": "hombre de 60 años con obesidad, quiere bajar de peso",
     "respuesta_referencia": "Obesidad. Calcular IMC, evaluar comorbilidades. Plan de alimentación y ejercicio gradual.",
     "nivel_atencion": "primer_nivel"},
]


# ─── MÉTRICAS (sin dependencias externas) ─────────────────────────────────────

def calcular_bleu(referencia: str, generada: str) -> float:
    """BLEU-1 unigrama simplificado"""
    ref = referencia.lower().split()
    gen = generada.lower().split()
    if not gen:
        return 0.0
    ref_counts = Counter(ref)
    matches = sum(min(count, ref_counts.get(word, 0)) for word, count in Counter(gen).items())
    precision = matches / len(gen)
    # Brevity penalty
    bp = 1.0 if len(gen) >= len(ref) else math.exp(1 - len(ref) / len(gen))
    return bp * precision


def calcular_rouge_l(referencia: str, generada: str) -> float:
    """ROUGE-L basado en subsecuencia común más larga (LCS)"""
    ref = referencia.lower().split()
    gen = generada.lower().split()
    if not ref or not gen:
        return 0.0
    # LCS dinámico
    m, n = len(ref), len(gen)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = dp[i-1][j-1] + 1 if ref[i-1] == gen[j-1] else max(dp[i-1][j], dp[i][j-1])
    lcs = dp[m][n]
    precision = lcs / n
    recall = lcs / m
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def intervalo_wilson(p: float, n: int, z: float = 1.96) -> tuple:
    """Intervalo de confianza de Wilson al 95%"""
    denom = 1 + z**2 / n
    centro = (p + z**2 / (2 * n)) / denom
    margen = (z * ((p * (1 - p) / n + z**2 / (4 * n**2)) ** 0.5)) / denom
    return round(max(0, centro - margen), 3), round(min(1, centro + margen), 3)


# ─── SIMULACIÓN DEL CHATBOT ────────────────────────────────────────────────────

def chatbot_responder(sintomas: str) -> tuple:
    """
    *** REEMPLAZAR ESTA FUNCIÓN CON EL MODELO REAL ***

    En producción:
        from modelo import chatbot
        respuesta, nivel = chatbot.generate(sintomas)

    Por ahora simula respuestas basadas en palabras clave.
    """
    urgencia_kw  = ["morados", "rigido", "confusion", "melena", "ictericia",
                    "sangre", "saturacion 92", "380", "200/120", "apendicitis",
                    "peritonitis", "hemoptisis", "edema en piernas"]
    referencia_kw = ["sibilancias", "3 semanas", "pérdida de peso", "asma",
                     "crónica", "cronica", "flema amarilla", "diarrea con sangre"]

    s = sintomas.lower()
    nivel = "primer_nivel"
    for kw in urgencia_kw:
        if kw in s:
            nivel = "urgencia"
            break
    if nivel == "primer_nivel":
        for kw in referencia_kw:
            if kw in s:
                nivel = "referencia"
                break

    respuesta = (f"Evaluación clínica: paciente con {sintomas[:50]}. "
                 f"Se recomienda manejo de {nivel.replace('_', ' ')} con seguimiento.")
    return respuesta, nivel


# ─── EVALUACIÓN PRINCIPAL ─────────────────────────────────────────────────────

def evaluar():
    print("=" * 65)
    print("  EVALUACIÓN DEL CHATBOT MÉDICO")
    print("  Chatbot médico SLM — UNIR Maestría en IA")
    print("=" * 65)

    resultados = []
    for caso in CASOS:
        respuesta_bot, nivel_bot = chatbot_responder(caso["sintomas"])
        bleu  = calcular_bleu(caso["respuesta_referencia"], respuesta_bot)
        rouge = calcular_rouge_l(caso["respuesta_referencia"], respuesta_bot)
        nivel_ok = nivel_bot == caso["nivel_atencion"]

        # Exactitud clínica: en producción = evaluación del médico (1/0)
        # Aquí se simula con semilla fija para reproducibilidad
        random.seed(hash(caso["id"]) % (2**32))
        exactitud = random.random() < 0.82

        resultados.append({
            "id": caso["id"],
            "categoria": caso["categoria"],
            "nivel_esperado": caso["nivel_atencion"],
            "nivel_bot": nivel_bot,
            "nivel_correcto": nivel_ok,
            "bleu": round(bleu, 4),
            "rouge_l": round(rouge, 4),
            "exactitud_clinica": exactitud,
        })

    n = len(resultados)
    exactitud_global  = sum(r["exactitud_clinica"] for r in resultados) / n
    concordancia      = sum(r["nivel_correcto"]    for r in resultados) / n
    bleu_prom         = sum(r["bleu"]              for r in resultados) / n
    rouge_prom        = sum(r["rouge_l"]           for r in resultados) / n

    ic_exc = intervalo_wilson(exactitud_global, n)
    ic_con = intervalo_wilson(concordancia,     n)

    print(f"\n  Casos evaluados: {n}")
    print(f"\n{'─'*65}")
    print(f"  {'Métrica':<35} {'Valor':>8}   IC 95%")
    print(f"{'─'*65}")
    print(f"  {'Exactitud clínica':<35} {exactitud_global:>7.1%}   [{ic_exc[0]:.1%}, {ic_exc[1]:.1%}]")
    print(f"  {'Concordancia nivel de atención':<35} {concordancia:>7.1%}   [{ic_con[0]:.1%}, {ic_con[1]:.1%}]")
    print(f"  {'BLEU (complementario)':<35} {bleu_prom:>7.3f}")
    print(f"  {'ROUGE-L (complementario)':<35} {rouge_prom:>7.3f}")
    print(f"{'─'*65}")

    print(f"\n  RESULTADOS POR CATEGORÍA")
    print(f"  {'Categoría':<20} {'Exactitud':>10} {'Concordancia':>14}   n")
    print(f"  {'─'*50}")
    for cat in ["respiratorio", "gastrointestinal", "cronico", "preventivo"]:
        sub = [r for r in resultados if r["categoria"] == cat]
        exc = sum(r["exactitud_clinica"] for r in sub) / len(sub)
        con = sum(r["nivel_correcto"]    for r in sub) / len(sub)
        print(f"  {cat.capitalize():<20} {exc:>9.0%}  {con:>13.0%}   {len(sub)}")

    print(f"\n  CRITERIOS DE ÉXITO")
    print(f"  Exactitud  ≥ 80%:   {'✓ CUMPLE' if exactitud_global >= 0.80 else '✗ NO CUMPLE':12s} ({exactitud_global:.1%})")
    print(f"  Concordancia ≥ 75%: {'✓ CUMPLE' if concordancia   >= 0.75 else '✗ NO CUMPLE':12s} ({concordancia:.1%})")

    print(f"\n  ⚠  Resultados simulados — reemplazar chatbot_responder()")
    print(f"     con el modelo real para obtener métricas definitivas.")
    print("=" * 65)

    with open("resultados_evaluacion.json", "w", encoding="utf-8") as f:
        json.dump({
            "n_casos": n,
            "exactitud_clinica":  round(exactitud_global, 4),
            "ic_exactitud":       list(ic_exc),
            "concordancia_nivel": round(concordancia, 4),
            "ic_concordancia":    list(ic_con),
            "bleu_promedio":      round(bleu_prom, 4),
            "rouge_l_promedio":   round(rouge_prom, 4),
            "detalle":            resultados,
        }, f, ensure_ascii=False, indent=2)
    print("\n  Resultados guardados en: resultados_evaluacion.json\n")


if __name__ == "__main__":
    evaluar()
