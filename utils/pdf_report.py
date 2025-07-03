"""
Utilidad para generar reportes PDF del sistema de simulación de drones
"""
import io
import os
import tempfile
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import pandas as pd
import numpy as np

class PDFReportGenerator:
    """Generador de reportes PDF para la simulación de drones"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        # Crear directorio temporal para imágenes
        self.temp_dir = tempfile.mkdtemp()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados para el PDF"""
        # Estilo para título principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            textColor=HexColor('#2E86AB'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=HexColor('#A23B72'),
            spaceBefore=20,
            spaceAfter=12
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6
        ))
    
    def generate_simulation_report(self, simulation_data, output_path=None):
        """Genera el reporte completo de la simulación"""
        if output_path is None:
            output_path = f"reporte_simulacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Crear buffer para el PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        try:
            # Título del reporte
            story.append(Paragraph("🚁 Reporte de Simulación Logística de Drones", self.styles['CustomTitle']))
            story.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", self.styles['CustomNormal']))
            story.append(Spacer(1, 20))
            
            # 1. Tabla de clientes
            story.extend(self._create_clients_table(simulation_data.get('clients', [])))
            story.append(PageBreak())
            
            # 2. Tabla de órdenes
            story.extend(self._create_orders_table(simulation_data.get('orders', [])))
            story.append(PageBreak())
            
            # 3. Gráficos
            story.extend(self._create_charts_section(simulation_data))
            
            # Construir PDF
            doc.build(story)
            
            # Si se especifica un path, guardar el archivo
            if output_path and not output_path.startswith('temp_'):
                with open(output_path, 'wb') as f:
                    f.write(buffer.getvalue())
            
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            # En caso de error, crear un PDF básico sin gráficos
            return self._create_basic_report(simulation_data, buffer, doc)
        finally:
            # Limpiar archivos temporales
            self._cleanup_temp_files()
    
    def _create_basic_report(self, simulation_data, buffer, doc):
        """Crea un reporte básico sin gráficos en caso de error"""
        story = []
        
        # Título del reporte
        story.append(Paragraph("🚁 Reporte de Simulación Logística de Drones", self.styles['CustomTitle']))
        story.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", self.styles['CustomNormal']))
        story.append(Paragraph("(Versión simplificada - Error en gráficos)", self.styles['CustomNormal']))
        story.append(Spacer(1, 20))
        
        # Solo tablas
        story.extend(self._create_clients_table(simulation_data.get('clients', [])))
        story.append(PageBreak())
        story.extend(self._create_orders_table(simulation_data.get('orders', [])))
        
        # Construir PDF básico
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _cleanup_temp_files(self):
        """Limpia archivos temporales"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning temp files: {e}")

    def _create_clients_table(self, clients_data):
        """Crea la tabla de clientes"""
        story = []
        story.append(Paragraph("📋 1. Tabla de Clientes", self.styles['CustomHeading']))
        
        if not clients_data:
            story.append(Paragraph("No hay datos de clientes disponibles.", self.styles['CustomNormal']))
            return story
        
        # Preparar datos para la tabla
        table_data = [['ID', 'Nombre', 'Tipo', 'Total Órdenes', 'Nodo ID']]
        
        for client in clients_data:
            table_data.append([
                str(client.get('ID', client.get('client_id', 'N/A'))),
                client.get('Nombre', client.get('name', 'N/A')),
                client.get('Tipo', client.get('type', 'Cliente')),
                str(client.get('Total Pedidos', client.get('total_orders', 0))),
                str(client.get('Nodo ID', client.get('node_id', 'N/A')))
            ])
        
        # Crear tabla
        table = Table(table_data, colWidths=[1*inch, 2*inch, 1.5*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#FFFFFF')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#DDDDDD'))
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        # Resumen de clientes
        total_clients = len(clients_data)
        total_orders = sum(client.get('Total Pedidos', client.get('total_orders', 0)) for client in clients_data)
        
        summary_text = f"<b>Resumen:</b> {total_clients} clientes registrados con un total de {total_orders} órdenes."
        story.append(Paragraph(summary_text, self.styles['CustomNormal']))
        
        return story
    
    def _create_orders_table(self, orders_data):
        """Crea la sección de órdenes en formato JSON"""
        story = []
        story.append(Paragraph("📦 2. Datos de Órdenes (Formato API)", self.styles['CustomHeading']))
        
        if not orders_data:
            story.append(Paragraph("No hay datos de órdenes disponibles.", self.styles['CustomNormal']))
            return story
        
        # Mostrar órdenes en formato JSON-like
        story.append(Paragraph("Formato de datos como respuesta de API:", self.styles['CustomNormal']))
        story.append(Spacer(1, 10))
        
        # Crear texto formateado para cada orden
        for i, order in enumerate(orders_data):
            order_json = f"""{{
    "ID": {order.get('ID', order.get('order_id', 'N/A'))},
    "Cliente_ID": {order.get('Cliente ID', order.get('client_id', 'N/A'))},
    "Origen": "{order.get('Origen', order.get('origin', 'N/A'))}",
    "Destino": "{order.get('Destino', order.get('destination', 'N/A'))}",
    "Status": "{order.get('Status', order.get('status', 'N/A'))}",
    "Prioridad": {order.get('Prioridad', order.get('priority', 'N/A'))},
    "Fecha_Creacion": "{order.get('Fecha Creación', order.get('created_at', 'N/A'))}",
    "Fecha_Entrega": "{order.get('Fecha Entrega', order.get('delivered_at', 'N/A'))}",
    "Costo_Ruta": {order.get('Costo Total', order.get('total_cost', 0))}
}}"""
            
            # Agregar cada orden como párrafo con estilo de código
            story.append(Paragraph(f"<b>Orden {i+1}:</b>", self.styles['CustomNormal']))
            
            # Crear estilo para código
            code_style = ParagraphStyle(
                name='CodeStyle',
                parent=self.styles['Normal'],
                fontSize=8,
                fontName='Courier',
                leftIndent=20,
                backgroundColor=HexColor('#F5F5F5'),
                borderColor=HexColor('#DDDDDD'),
                borderWidth=1,
                borderPadding=5
            )
            
            story.append(Paragraph(order_json.replace('\n', '<br/>'), code_style))
            story.append(Spacer(1, 15))
            
            # Limitar a 10 órdenes para no sobrecargar el PDF
            if i >= 9:
                remaining = len(orders_data) - 10
                if remaining > 0:
                    story.append(Paragraph(f"... y {remaining} órdenes adicionales", self.styles['CustomNormal']))
                break
        
        # Resumen de órdenes
        total_orders = len(orders_data)
        pending_orders = len([o for o in orders_data if o.get('Status', o.get('status')) == 'Pendiente'])
        completed_orders = len([o for o in orders_data if o.get('Status', o.get('status')) == 'Entregado'])
        
        story.append(Spacer(1, 20))
        summary_text = f"<b>Resumen de Órdenes:</b> {total_orders} órdenes totales ({pending_orders} pendientes, {completed_orders} completadas)."
        story.append(Paragraph(summary_text, self.styles['CustomNormal']))
        
        return story
    
    def _create_charts_section(self, simulation_data):
        """Crea la sección de gráficos"""
        story = []
        story.append(Paragraph("📊 3. Análisis Gráfico", self.styles['CustomHeading']))
        
        # 3.1 Gráfico de distribución de nodos (pie chart)
        story.extend(self._create_node_distribution_chart(simulation_data))
        story.append(PageBreak())
        
        # 3.2 Gráfico de clientes más visitados
        story.extend(self._create_visits_charts(simulation_data))
        
        return story
    
    def _create_node_distribution_chart(self, simulation_data):
        """Crea gráfico de distribución de nodos"""
        story = []
        story.append(Paragraph("🥧 3.1 Distribución de Nodos por Tipo", self.styles['CustomHeading']))
        
        network_stats = simulation_data.get('summary', {}).get('network_stats', {})
        
        if network_stats:
            try:
                # Datos para el gráfico
                labels = ['📦 Almacenamiento', '🔋 Recarga', '👤 Clientes']
                sizes = [
                    network_stats.get('storage', {}).get('count', 0),
                    network_stats.get('charging', {}).get('count', 0),
                    network_stats.get('client', {}).get('count', 0)
                ]
                colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
                
                # Verificar que hay datos válidos
                if sum(sizes) == 0:
                    story.append(Paragraph("No hay datos válidos de distribución de nodos.", self.styles['CustomNormal']))
                    return story
                
                # Crear gráfico
                plt.figure(figsize=(8, 6))
                wedges, texts, autotexts = plt.pie(sizes, labels=labels, colors=colors, 
                                                 autopct='%1.1f%%', startangle=90)
                
                plt.title('Distribución de Nodos por Tipo', fontsize=14, fontweight='bold')
                
                # Guardar como imagen temporal en directorio temporal
                img_path = os.path.join(self.temp_dir, f"pie_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                plt.savefig(img_path, dpi=300, bbox_inches='tight', format='png')
                plt.close()
                
                # Verificar que el archivo se creó correctamente
                if os.path.exists(img_path):
                    # Agregar imagen al PDF
                    story.append(Image(img_path, width=6*inch, height=4.5*inch))
                    story.append(Spacer(1, 20))
                    
                    # Agregar texto explicativo
                    total_nodes = sum(sizes)
                    if total_nodes > 0:
                        explanation = f"La red cuenta con {total_nodes} nodos distribuidos en: {sizes[0]} nodos de almacenamiento ({sizes[0]/total_nodes*100:.1f}%), {sizes[1]} estaciones de recarga ({sizes[1]/total_nodes*100:.1f}%), y {sizes[2]} clientes ({sizes[2]/total_nodes*100:.1f}%)."
                        story.append(Paragraph(explanation, self.styles['CustomNormal']))
                else:
                    story.append(Paragraph("Error al generar el gráfico de distribución de nodos.", self.styles['CustomNormal']))
                
            except Exception as e:
                print(f"Error creating pie chart: {e}")
                story.append(Paragraph("Error al generar el gráfico de distribución de nodos.", self.styles['CustomNormal']))
        else:
            story.append(Paragraph("No hay datos de distribución de nodos disponibles.", self.styles['CustomNormal']))
        
        return story
    
    def _create_visits_charts(self, simulation_data):
        """Crea gráficos de nodos más visitados"""
        story = []
        story.append(Paragraph("📈 3.2 Análisis de Nodos Más Visitados", self.styles['CustomHeading']))
        
        visit_stats = simulation_data.get('visit_statistics', {})
        
        # Crear gráficos para cada tipo de nodo
        chart_types = [
            ('clients', '👤 Clientes Más Visitados', '#45B7D1'),
            ('recharges', '🔋 Estaciones de Recarga Más Visitadas', '#4ECDC4'),
            ('storages', '📦 Nodos de Almacenamiento Más Visitados', '#FF6B6B')
        ]
        
        for chart_type, title, color in chart_types:
            data = visit_stats.get(chart_type, [])
            
            if data and len(data) > 0:
                try:
                    # Tomar top 5
                    top_data = data[:5]
                    names = [item['name'] for item in top_data]
                    visits = [item['visits'] for item in top_data]
                    
                    if len(names) > 0 and max(visits) > 0:
                        # Crear gráfico de barras
                        plt.figure(figsize=(10, 6))
                        bars = plt.bar(range(len(names)), visits, color=color, alpha=0.8)
                        
                        plt.xlabel('Nodos')
                        plt.ylabel('Número de Visitas')
                        plt.title(title, fontsize=14, fontweight='bold')
                        plt.xticks(range(len(names)), names, rotation=45, ha='right')
                        
                        # Agregar valores sobre las barras
                        for bar, value in zip(bars, visits):
                            height = bar.get_height()
                            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                   f'{value}', ha='center', va='bottom', fontweight='bold')
                        
                        plt.tight_layout()
                        
                        # Guardar como imagen temporal
                        img_path = os.path.join(self.temp_dir, f"{chart_type}_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                        plt.savefig(img_path, dpi=300, bbox_inches='tight', format='png')
                        plt.close()
                        
                        # Verificar que el archivo se creó correctamente
                        if os.path.exists(img_path):
                            # Agregar al PDF
                            story.append(Paragraph(title, self.styles['CustomHeading']))
                            story.append(Image(img_path, width=7*inch, height=4*inch))
                            story.append(Spacer(1, 10))
                            
                            # Texto explicativo
                            if visits:
                                max_visits = max(visits)
                                most_visited = names[visits.index(max_visits)]
                                explanation = f"El nodo más visitado en esta categoría es '{most_visited}' con {max_visits} visitas."
                                story.append(Paragraph(explanation, self.styles['CustomNormal']))
                        else:
                            story.append(Paragraph(f"{title}: Error al generar gráfico.", self.styles['CustomNormal']))
                    else:
                        story.append(Paragraph(f"{title}: No hay datos de visitas válidos.", self.styles['CustomNormal']))
                        
                    story.append(Spacer(1, 20))
                    
                except Exception as e:
                    print(f"Error creating {chart_type} chart: {e}")
                    story.append(Paragraph(f"{title}: Error al generar gráfico.", self.styles['CustomNormal']))
                    story.append(Spacer(1, 10))
            else:
                story.append(Paragraph(f"{title}: No hay datos de visitas disponibles.", self.styles['CustomNormal']))
                story.append(Spacer(1, 10))
        
        return story

# Función de utilidad para generar reporte desde datos de simulación
def generate_pdf_report(simulation_data, output_path=None):
    """Función de utilidad para generar reporte PDF"""
    generator = PDFReportGenerator()
    return generator.generate_simulation_report(simulation_data, output_path)