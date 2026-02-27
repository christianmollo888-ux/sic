from datetime import date
from backend.database import SessionLocal, engine, Base
from backend import models_forms

def seed_form_200_v6():
    db = SessionLocal()
    try:
        # 1. Create Form Version
        form_v6 = db.query(models_forms.FormVersion).filter_by(form_code="200", version_number="6").first()
        if not form_v6:
            form_v6 = models_forms.FormVersion(
                form_code="200",
                version_number="6",
                effective_from=date(2025, 1, 1),
                is_active=True
            )
            db.add(form_v6)
            db.flush()
            print("Created Form 200 v6")
        else:
            print("Form 200 v6 already exists")

        # 2. Define Fields (from PDF analysis)
        fields = [
            # Rubro 1
            ("Rubro 1", "13", "Ventas de bienes y/o servicios gravados en el mercado interno", False, None),
            ("Rubro 1", "14", "Exportación de bienes y operaciones exentas", False, None),
            ("Rubro 1", "15", "Ventas gravadas a Tasa Cero", False, None),
            ("Rubro 1", "505", "Ventas no gravadas y operaciones que no son objeto del IVA", False, None),
            ("Rubro 1", "16", "Valor atribuido a bienes y/o servicios retirados y consumos particulares", False, None),
            ("Rubro 1", "17", "Devoluciones y rescisiones efectuadas en el período", False, None),
            ("Rubro 1", "18", "Descuentos, bonificaciones y rebajas obtenidas en el período", False, None),
            ("Rubro 1", "39", "Débito Fiscal (C13+C16+C17+C18)*13%", True, "(C13 + C16 + C17 + C18) * 0.13"),
            ("Rubro 1", "55", "Débito Fiscal actualizado correspondiente a reintegros", False, None),
            ("Rubro 1", "19", "Débito Fiscal actualizado correspondiente a Conciliaciones", False, None),
            ("Rubro 1", "1002", "Total Débito Fiscal del período", True, "C39 + C55 + C19"),
            
            # Rubro 2
            ("Rubro 2", "11", "Total Compras correspondientes a actividades gravadas y/o no gravadas", False, None),
            ("Rubro 2", "26", "Compra directamente vinculadas a actividad gravada", False, None),
            ("Rubro 2", "31", "Compras en las que no es posible discriminar su vinculación", False, None),
            ("Rubro 2", "27", "Devoluciones y rescisiones recibidas en el período", False, None),
            ("Rubro 2", "28", "Descuentos, bonificaciones y rebajas otorgadas en el período", False, None),
            ("Rubro 2", "114", "Crédito Fiscal correspondiente a: ((C26 + C27 + C28) * 13%)", True, "(C26 + C27 + C28) * 0.13"),
            ("Rubro 2", "30", "Crédito fiscal actualizado correspondiente a Conciliaciones", False, None),
            ("Rubro 2", "1003", "Crédito fiscal proporcional correspondiente a la actividad gravada", False, None),
            ("Rubro 2", "1004", "Total Crédito Fiscal del periodo (C114+C30+C1003)", True, "C114 + C30 + C1003"),
            
            # Rubro 3
            ("Rubro 3", "693", "Diferencia a favor del Contribuyente (C1004 - C1002; Si >0)", True, "GREATEST(0, C1004 - C1002)"),
            ("Rubro 3", "909", "Diferencia a favor del Fisco o Impuesto Determinado (C1002 - C1004; Si > 0)", True, "GREATEST(0, C1002 - C1004)"),
            ("Rubro 3", "635", "Importe Utilizado Del Saldo De Crédito Fiscal Actualizado", False, None),
            ("Rubro 3", "1001", "Saldo de Impuesto Determinado a favor del Fisco (C909-C635;Si > 0)", True, "GREATEST(0, C909 - C635)"),
            ("Rubro 3", "621", "Pago a cuenta del 50% de contribuciones patronales pagadas del periodo", False, None),
            ("Rubro 3", "629", "Saldo a favor del Fisco despues de compensar pagos a cuenta por contribuciones patronales", False, None),
            ("Rubro 3", "622", "Importe Utilizado De Pagos a Cuenta Realizados en el Periodo", False, None),
            ("Rubro 3", "640", "Importe Utilizado del Saldo de Pagos a Cuenta", False, None),
            ("Rubro 3", "468", "Saldo a favor del fisco despues de compensar pagos a cuenta (C629-C622-C640; Si > 0)", True, "GREATEST(0, C629 - C622 - C640)"),
            ("Rubro 3", "465", "Pago a cuenta del 5% por compras a contribuyentes del SIETE- RG", False, None),
            ("Rubro 3", "466", "Importe Utilizado De Pagos A Cuenta Por Compras a Contribuyentes Del Siete - RG", False, None),
            ("Rubro 3", "996", "Saldo a favor del Fisco (C468-C465-C466; Si > 0)", True, "GREATEST(0, C468 - C465 - C466)"),
        ]

        for rubric, code, label, is_calc, formula in fields:
            field = db.query(models_forms.FormFieldDefinition).filter_by(
                version_id=form_v6.id, field_code=code
            ).first()
            if not field:
                field = models_forms.FormFieldDefinition(
                    version_id=form_v6.id,
                    rubric=rubric,
                    field_code=code,
                    label=label,
                    is_calculated=is_calc,
                    formula=formula
                )
                db.add(field)
                print(f"Added field {code}: {label}")

        db.commit()
        print("Seeding completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    seed_form_200_v6()
