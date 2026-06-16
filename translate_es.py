#!/usr/bin/env python3
"""
Genera messages_es.csv para módulos Axelor a partir de messages_en.csv.
Usa un diccionario ERP extenso + traducción palabra-por-palabra como fallback.
Solo traduce strings de UI (etiquetas, menús, mensajes al usuario).
"""
import csv
import re
import os
import glob

# ─── Diccionario ERP completo EN→ES ──────────────────────────────────────────
DICT = {
    # Acciones generales
    "Save": "Guardar", "Cancel": "Cancelar", "Confirm": "Confirmar",
    "Delete": "Eliminar", "Edit": "Editar", "Search": "Buscar",
    "Add": "Agregar", "Remove": "Quitar", "Close": "Cerrar",
    "New": "Nuevo", "Create": "Crear", "Update": "Actualizar",
    "Refresh": "Actualizar", "Reset": "Restablecer", "Clear": "Limpiar",
    "Import": "Importar", "Export": "Exportar", "Print": "Imprimir",
    "Download": "Descargar", "Upload": "Cargar", "Open": "Abrir",
    "View": "Ver", "Show": "Mostrar", "Hide": "Ocultar",
    "Enable": "Activar", "Disable": "Desactivar", "Activate": "Activar",
    "Deactivate": "Desactivar", "Archive": "Archivar", "Unarchive": "Desarchivar",
    "Validate": "Validar", "Reject": "Rechazar", "Approve": "Aprobar",
    "Submit": "Enviar", "Send": "Enviar", "Generate": "Generar",
    "Calculate": "Calcular", "Compute": "Calcular", "Process": "Procesar",
    "Post": "Contabilizar", "Simulate": "Simular", "Duplicate": "Duplicar",
    "Copy": "Copiar", "Move": "Mover", "Transfer": "Transferir",
    "Merge": "Fusionar", "Split": "Dividir", "Link": "Vincular",
    "Unlink": "Desvincular", "Lock": "Bloquear", "Unlock": "Desbloquear",
    "Sign": "Firmar", "Reconcile": "Conciliar", "Reverse": "Revertir",
    "Revert": "Revertir", "Undo": "Deshacer", "Redo": "Rehacer",
    "Next": "Siguiente", "Previous": "Anterior", "Back": "Volver",
    "Finish": "Finalizar", "Complete": "Completar", "Start": "Iniciar",
    "Stop": "Detener", "Pause": "Pausar", "Resume": "Reanudar",
    "Launch": "Lanzar", "Execute": "Ejecutar", "Run": "Ejecutar",
    "Schedule": "Programar", "Plan": "Planificar", "Assign": "Asignar",
    "Reallocate": "Reasignar", "Configure": "Configurar", "Install": "Instalar",
    "Select": "Seleccionar", "Deselect": "Deseleccionar", "Check": "Verificar",
    "Uncheck": "Desmarcar", "Toggle": "Alternar", "Expand": "Expandir",
    "Collapse": "Colapsar", "Load": "Cargar", "Reload": "Recargar",
    "Apply": "Aplicar", "Preview": "Vista previa", "Test": "Probar",

    # Campos comunes
    "Name": "Nombre", "Description": "Descripción", "Code": "Código",
    "Reference": "Referencia", "Number": "Número", "Date": "Fecha",
    "Type": "Tipo", "Status": "Estado", "Stage": "Etapa",
    "Category": "Categoría", "Tag": "Etiqueta", "Note": "Nota",
    "Notes": "Notas", "Comment": "Comentario", "Comments": "Comentarios",
    "Attachment": "Adjunto", "Attachments": "Adjuntos",
    "Active": "Activo", "Inactive": "Inactivo", "Archived": "Archivado",
    "Required": "Requerido", "Optional": "Opcional", "Mandatory": "Obligatorio",
    "Default": "Por defecto", "Sequence": "Secuencia", "Order": "Orden",
    "Priority": "Prioridad", "Color": "Color", "Image": "Imagen",
    "Logo": "Logotipo", "Language": "Idioma", "Currency": "Moneda",
    "Country": "País", "City": "Ciudad", "Zip": "Código postal",
    "Zip Code": "Código postal", "Address": "Dirección", "Street": "Calle",
    "Phone": "Teléfono", "Mobile": "Celular", "Fax": "Fax",
    "Email": "Correo electrónico", "Website": "Sitio web",
    "Timezone": "Zona horaria", "Locale": "Configuración regional",

    # Personas / Contactos
    "Partner": "Socio/Contacto", "Partners": "Socios/Contactos",
    "Customer": "Cliente", "Customers": "Clientes",
    "Supplier": "Proveedor", "Suppliers": "Proveedores",
    "Vendor": "Proveedor", "Contact": "Contacto", "Contacts": "Contactos",
    "Employee": "Empleado", "Employees": "Empleados",
    "User": "Usuario", "Users": "Usuarios",
    "Manager": "Gerente", "Director": "Director",
    "Responsible": "Responsable", "Assigned to": "Asignado a",
    "Created by": "Creado por", "Updated by": "Actualizado por",
    "Title": "Título", "First Name": "Nombre", "Last Name": "Apellido",
    "Full Name": "Nombre completo", "Job Position": "Cargo",
    "Job Title": "Título del cargo", "Department": "Departamento",
    "Team": "Equipo", "Company": "Empresa", "Companies": "Empresas",
    "Organization": "Organización", "Group": "Grupo", "Groups": "Grupos",

    # Contabilidad
    "Invoice": "Factura", "Invoices": "Facturas",
    "Customer Invoice": "Factura de cliente",
    "Supplier Invoice": "Factura de proveedor",
    "Credit Note": "Nota de crédito", "Debit Note": "Nota de débito",
    "Payment": "Pago", "Payments": "Pagos",
    "Receipt": "Cobro", "Receipts": "Cobros",
    "Account": "Cuenta", "Accounts": "Cuentas",
    "Chart of Accounts": "Plan de cuentas",
    "Account Chart": "Plan de cuentas",
    "Journal": "Diario contable", "Journals": "Diarios contables",
    "Journal Entry": "Asiento contable", "Journal Entries": "Asientos contables",
    "Move": "Asiento", "Moves": "Asientos",
    "Move Line": "Línea de asiento", "Move Lines": "Líneas de asiento",
    "Balance": "Saldo", "Debit": "Débito", "Credit": "Crédito",
    "Tax": "Impuesto", "Taxes": "Impuestos",
    "VAT": "IVA", "Tax Line": "Línea de impuesto",
    "Fiscal Year": "Ejercicio fiscal", "Period": "Período", "Periods": "Períodos",
    "Closing": "Cierre", "Opening": "Apertura",
    "Reconciliation": "Conciliación", "Reconcile": "Conciliar",
    "Aged Balance": "Balance por antigüedad",
    "Due Date": "Fecha de vencimiento",
    "Payment Mode": "Modo de pago", "Payment Terms": "Condiciones de pago",
    "Payment Condition": "Condición de pago",
    "Analytic": "Analítico", "Analytic Account": "Cuenta analítica",
    "Cost Center": "Centro de costo",
    "Fixed Asset": "Activo fijo", "Fixed Assets": "Activos fijos",
    "Depreciation": "Depreciación", "Amortization": "Amortización",
    "Ledger": "Libro mayor", "General Ledger": "Mayor general",
    "Trial Balance": "Balance de comprobación",
    "Cash Register": "Caja", "Cash": "Efectivo",
    "Bank": "Banco", "Banks": "Bancos",
    "Bank Account": "Cuenta bancaria", "Bank Accounts": "Cuentas bancarias",
    "Bank Statement": "Extracto bancario",
    "Bank Reconciliation": "Conciliación bancaria",
    "Clearing": "Compensación", "Withholding": "Retención",
    "Withholding Tax": "Retención en la fuente",
    "Reversal": "Reversión", "Write-off": "Castigo contable",
    "Accrual": "Devengo", "Deferral": "Diferimiento",
    "Cutoff": "Corte contable", "Simulate": "Simular",
    "Outstanding": "Pendiente", "Overdue": "Vencido",
    "Draft": "Borrador", "Posted": "Contabilizado",
    "Validated": "Validado", "Canceled": "Cancelado",
    "Refund": "Reembolso", "Advance": "Anticipo",
    "Deposit": "Depósito", "Deposit Slip": "Comprobante de depósito",
    "Expense": "Gasto", "Expenses": "Gastos",
    "Revenue": "Ingresos", "Income": "Ingreso",
    "Profit": "Ganancia", "Loss": "Pérdida",
    "Asset": "Activo", "Assets": "Activos",
    "Liability": "Pasivo", "Liabilities": "Pasivos",
    "Equity": "Patrimonio",
    "Gross": "Bruto", "Net": "Neto",
    "Amount": "Monto", "Total": "Total", "Subtotal": "Subtotal",
    "Tax Amount": "Monto de impuesto",
    "Unit Price": "Precio unitario", "Quantity": "Cantidad",
    "Discount": "Descuento", "Price": "Precio",
    "Rate": "Tasa", "Percentage": "Porcentaje",
    "Exchange Rate": "Tipo de cambio",

    # Ventas y Compras
    "Sale Order": "Pedido de venta", "Sale Orders": "Pedidos de venta",
    "Sales Order": "Pedido de venta", "Sales Orders": "Pedidos de venta",
    "Quotation": "Cotización", "Quotations": "Cotizaciones",
    "Purchase Order": "Orden de compra", "Purchase Orders": "Órdenes de compra",
    "Request for Quotation": "Solicitud de cotización",
    "Purchase Requisition": "Requisición de compra",
    "Price List": "Lista de precios", "Price Lists": "Listas de precios",
    "Pricelist": "Lista de precios",
    "Product": "Producto", "Products": "Productos",
    "Product Category": "Categoría de producto",
    "Unit of Measure": "Unidad de medida", "Unit": "Unidad",
    "Delivery": "Entrega", "Deliveries": "Entregas",
    "Shipment": "Envío", "Shipping": "Envío",
    "Carrier": "Transportista", "Tracking": "Seguimiento",
    "Return": "Devolución", "Returns": "Devoluciones",
    "Subscription": "Suscripción", "Pack": "Paquete",
    "Cart": "Carrito", "Configurator": "Configurador",
    "Lead Time": "Tiempo de entrega",
    "Advance Payment": "Pago anticipado",

    # Inventario / Almacén
    "Warehouse": "Almacén", "Warehouses": "Almacenes",
    "Stock": "Stock/Inventario", "Inventory": "Inventario",
    "Stock Location": "Ubicación", "Location": "Ubicación",
    "Stock Move": "Movimiento de stock",
    "Stock Move Line": "Línea de movimiento",
    "Internal Move": "Movimiento interno",
    "Incoming": "Entrada", "Outgoing": "Salida",
    "Receipt": "Recepción", "Lot": "Lote",
    "Serial Number": "Número de serie",
    "Traceability": "Trazabilidad", "Tracking Number": "Número de seguimiento",
    "Available Qty": "Cantidad disponible",
    "Forecasted Qty": "Cantidad prevista",
    "Reorder Point": "Punto de reorden",
    "Min Qty": "Cantidad mínima", "Max Qty": "Cantidad máxima",
    "Putaway": "Almacenamiento", "Route": "Ruta",
    "Scrapping": "Desecho", "Scrap": "Desperdicio",
    "Landed Cost": "Costo de importación",

    # Producción
    "Manufacturing Order": "Orden de fabricación",
    "Manufacturing Orders": "Órdenes de fabricación",
    "Bill of Materials": "Lista de materiales",
    "Work Center": "Centro de trabajo", "Work Centers": "Centros de trabajo",
    "Operation": "Operación", "Operations": "Operaciones",
    "Routing": "Ruta de producción", "Workshop": "Taller",
    "Work-in-Progress": "Trabajo en proceso",
    "Finished Product": "Producto terminado",
    "Raw Material": "Materia prima", "By-product": "Subproducto",
    "Capacity": "Capacidad", "Machine": "Máquina",
    "Cycle Time": "Tiempo de ciclo",
    "Subcontract": "Subcontratación",
    "MRP": "MRP", "Production Planning": "Planificación de producción",

    # RRHH
    "Leave": "Permiso", "Leave Request": "Solicitud de permiso",
    "Leave Type": "Tipo de permiso",
    "Annual Leave": "Vacaciones anuales",
    "Sick Leave": "Licencia por enfermedad",
    "Timesheet": "Registro de horas", "Timesheets": "Registros de horas",
    "Working Hours": "Jornada laboral",
    "Overtime": "Horas extras", "Bonus": "Bono",
    "Salary": "Salario", "Payroll": "Nómina",
    "Payslip": "Recibo de nómina", "Payslips": "Recibos de nómina",
    "Contract": "Contrato", "Contracts": "Contratos",
    "Position": "Cargo", "Skill": "Habilidad", "Skills": "Habilidades",
    "Training": "Capacitación", "Recruitment": "Reclutamiento",
    "Applicant": "Candidato", "Job Offer": "Oferta de trabajo",
    "Interview": "Entrevista", "Appraisal": "Evaluación de desempeño",

    # Proyectos / CRM
    "Project": "Proyecto", "Projects": "Proyectos",
    "Task": "Tarea", "Tasks": "Tareas",
    "Milestone": "Hito", "Phase": "Fase",
    "Sprint": "Sprint", "Gantt": "Gantt",
    "Resource": "Recurso", "Assignment": "Asignación",
    "Progress": "Avance", "Deadline": "Fecha límite",
    "Lead": "Prospecto", "Leads": "Prospectos",
    "Opportunity": "Oportunidad", "Opportunities": "Oportunidades",
    "Pipeline": "Embudo de ventas",
    "Lost Reason": "Motivo de pérdida",
    "Expected Revenue": "Ingresos esperados",
    "Probability": "Probabilidad",
    "Call": "Llamada", "Meeting": "Reunión", "Event": "Evento",
    "Campaign": "Campaña", "Source": "Origen",

    # UI / Sistema
    "Dashboard": "Panel de control", "Menu": "Menú",
    "Report": "Reporte", "Reports": "Reportes",
    "Configuration": "Configuración", "Settings": "Configuración",
    "Administration": "Administración",
    "Role": "Rol", "Roles": "Roles",
    "Permission": "Permiso", "Permissions": "Permisos",
    "Template": "Plantilla", "Templates": "Plantillas",
    "Sequence": "Secuencia", "Sequences": "Secuencias",
    "Scheduled Action": "Acción programada",
    "Batch": "Lote de proceso", "Job": "Tarea programada",
    "Translation": "Traducción", "Translations": "Traducciones",
    "Audit": "Auditoría", "Log": "Registro",
    "Message": "Mensaje", "Messages": "Mensajes",
    "Follower": "Seguidor", "Followers": "Seguidores",
    "Notification": "Notificación", "Notifications": "Notificaciones",
    "Alert": "Alerta", "Alerts": "Alertas",
    "Warning": "Advertencia", "Error": "Error", "Info": "Información",
    "Success": "Éxito", "Failure": "Fallo",
    "Help": "Ayuda", "Documentation": "Documentación",
    "List": "Lista", "Form": "Formulario", "Grid": "Cuadrícula",
    "Calendar": "Calendario", "Kanban": "Kanban", "Chart": "Gráfico",
    "Map": "Mapa", "Tree": "Árbol",
    "Filter": "Filtrar", "Sort": "Ordenar",
    "Favorite": "Favorito", "Favorites": "Favoritos",
    "History": "Historial", "Traceability": "Trazabilidad",
    "Yes": "Sí", "No": "No", "None": "Ninguno",
    "All": "Todos", "Other": "Otro",
    "From": "Desde", "To": "Hasta", "Of": "De",
    "Total": "Total", "Subtotal": "Subtotal",
    "Details": "Detalles", "Summary": "Resumen",
    "Overview": "Resumen general",
    "Information": "Información",
    "General": "General", "Advanced": "Avanzado",
    "Basic": "Básico", "Additional": "Adicional",
    "Main": "Principal", "Secondary": "Secundario",
    "Lines": "Líneas", "Line": "Línea",
    "Number of": "Número de",
    "by": "por", "for": "para", "from": "desde", "to": "hasta",
    "and": "y", "or": "o", "not": "no",

    # Estados
    "New": "Nuevo", "In Progress": "En proceso",
    "Done": "Completado", "Closed": "Cerrado",
    "Open": "Abierto", "Pending": "Pendiente",
    "Confirmed": "Confirmado", "Validated": "Validado",
    "Canceled": "Cancelado", "Cancelled": "Cancelado",
    "Rejected": "Rechazado", "Approved": "Aprobado",
    "Draft": "Borrador", "Posted": "Contabilizado",
    "Invoiced": "Facturado", "Paid": "Pagado",
    "Partial": "Parcial", "Overdue": "Vencido",
    "Expired": "Expirado", "Active": "Activo", "Inactive": "Inactivo",
    "Enabled": "Habilitado", "Disabled": "Deshabilitado",
    "Available": "Disponible", "Unavailable": "No disponible",
    "Locked": "Bloqueado", "Unlocked": "Desbloqueado",

    # Fechas y tiempo
    "Date": "Fecha", "Start Date": "Fecha de inicio",
    "End Date": "Fecha de fin", "Due Date": "Fecha de vencimiento",
    "Creation Date": "Fecha de creación",
    "Update Date": "Fecha de actualización",
    "Validation Date": "Fecha de validación",
    "Year": "Año", "Month": "Mes", "Week": "Semana", "Day": "Día",
    "Hour": "Hora", "Minute": "Minuto", "Second": "Segundo",
    "Duration": "Duración", "Period": "Período",
    "Deadline": "Fecha límite", "Anniversary": "Aniversario",

    # Mensajes comunes
    "Are you sure": "¿Está seguro",
    "Are you sure?": "¿Está seguro?",
    "Please select": "Por favor seleccione",
    "Please enter": "Por favor ingrese",
    "No record found": "No se encontraron registros",
    "No data": "Sin datos",
    "Loading": "Cargando",
    "Processing": "Procesando",
    "Saving": "Guardando",
    "Saved": "Guardado",
    "Deleted": "Eliminado",
    "Updated": "Actualizado",
    "Created": "Creado",
    "An error occurred": "Ocurrió un error",
    "Access denied": "Acceso denegado",
    "Not found": "No encontrado",
    "Invalid": "Inválido",
    "Valid": "Válido",
    "Mandatory field": "Campo obligatorio",
    "already exists": "ya existe",
    "does not exist": "no existe",
    "cannot be empty": "no puede estar vacío",
    "must be": "debe ser",
    "is required": "es requerido",
}

# ─── Términos que NO se traducen ─────────────────────────────────────────────
NO_TRANSLATE = {
    'PDF', 'CSV', 'API', 'XML', 'JSON', 'IBAN', 'BIC', 'BBAN', 'SIRET',
    'SIREN', 'RIB', 'TVA', 'ISO', 'ERP', 'CRM', 'MRP', 'BOM', 'SMTP',
    'IMAP', 'URL', 'ID', 'HTML', 'HTTP', 'HTTPS', 'SOAP', 'REST',
    'OAuth', 'SSO', 'CAS', 'LDAP', 'GDPR', 'RGPD', 'SLA', 'KPI',
    'ATI', 'WT', 'DMS', 'EDI', 'EAN', 'UPC', 'GTIN',
}

def should_skip(text):
    """Devuelve True si el texto no debe traducirse."""
    t = text.strip()
    if not t:
        return True
    # Solo números, símbolos, formatos
    if re.match(r'^[\d\s\.\,\%\#\$\€\+\-\*\/\(\)\[\]\{\}\_\:]+$', t):
        return True
    # Claves técnicas Java style (sin espacios, con puntos/camelCase)
    if re.match(r'^[a-z][a-zA-Z0-9]*\.[a-zA-Z]', t):
        return True
    # Código técnico puro (no tiene espacios y es corto)
    if len(t) <= 4 and t.upper() in NO_TRANSLATE:
        return True
    # Patrones de formato puro
    if re.match(r'^%[sdDfFMWY]+\s*[:=]?$', t):
        return True
    return False

def translate_text(text):
    """Traduce un string al español usando el diccionario."""
    if not text or should_skip(text):
        return text

    # 1. Coincidencia exacta (más rápido y correcto)
    if text in DICT:
        return DICT[text]

    # 2. Coincidencia exacta insensible a mayúsculas
    text_lower = text.lower()
    for k, v in DICT.items():
        if k.lower() == text_lower:
            return v

    # 3. Si el string tiene %s/%d (mensaje técnico con formato), no traducir parcialmente
    #    Solo traducir si hay una coincidencia exacta (ya cubierta arriba)
    if re.search(r'%[sdDfFMWY]', text):
        return text

    # 4. Para labels simples sin formato: sustituir frases con límites de palabra
    #    Solo aplica a strings cortos (etiquetas UI), no a párrafos largos
    if len(text) > 120:
        return text

    result = text
    # Ordenar por longitud descendente para sustituir frases largas primero
    sorted_dict = sorted(DICT.items(), key=lambda x: len(x[0]), reverse=True)
    for en, es in sorted_dict:
        if len(en) < 3:
            continue
        # Usar \b para límites de palabra — evita "Process" dentro de "processed"
        try:
            pattern = re.compile(r'\b' + re.escape(en) + r'\b', re.IGNORECASE)
            new_result = pattern.sub(es, result)
            if new_result != result:
                result = new_result
        except re.error:
            continue

    return result

def process_row(row):
    """Procesa una fila CSV y devuelve la versión española."""
    if len(row) < 1:
        return row

    key = row[0]
    message = row[1] if len(row) > 1 else ''

    # Texto a traducir: si hay mensaje lo usamos, si no usamos la clave
    source = message if message.strip() else key

    translated = translate_text(source)

    return [key, translated, '', '']

def process_file(en_path, es_path):
    """Procesa un archivo EN y genera el ES correspondiente."""
    if not os.path.exists(en_path):
        print(f"  SKIP (no existe): {en_path}")
        return

    rows_out = []
    with open(en_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, quotechar='"', skipinitialspace=True)
        for i, row in enumerate(reader):
            if i == 0:
                # Encabezado
                rows_out.append(['"key"', '"message"', '"comment"', '"context"'])
                continue
            if not row:
                continue
            processed = process_row(row)
            rows_out.append(processed)

    with open(es_path, 'w', encoding='utf-8', newline='') as f:
        for row in rows_out:
            if row == ['"key"', '"message"', '"comment"', '"context"']:
                f.write('"key","message","comment","context"\n')
            else:
                parts = []
                for cell in row:
                    escaped = str(cell).replace('"', '""')
                    parts.append(f'"{escaped}"')
                f.write(','.join(parts) + '\n')

    print(f"  OK ({len(rows_out)-1} strings): {es_path}")

# ─── Módulos a procesar ───────────────────────────────────────────────────────
BASE = '/home/alvarto/bitacora/www/axelor'

MODULES = [
    'axelor-account',
    'axelor-base',
]

print("Generando traducciones al español...\n")
for module in MODULES:
    i18n_dir = f"{BASE}/{module}/src/main/resources/i18n"
    en_file = f"{i18n_dir}/messages_en.csv"
    es_file = f"{i18n_dir}/messages_es.csv"
    print(f"Módulo: {module}")
    process_file(en_file, es_file)

print("\nListo.")
