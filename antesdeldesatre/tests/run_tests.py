"""
Script para ejecutar todas las pruebas del sistema de generación de grafos

Ejecuta tanto pruebas unitarias como de integración y genera un reporte completo.
"""

import unittest
import sys
import os
import time
from io import StringIO

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def ejecutar_todas_las_pruebas():
    """Ejecuta todas las pruebas y genera un reporte"""
    print("=" * 70)
    print("EJECUTANDO SUITE COMPLETA DE PRUEBAS")
    print("Sistema de Generación y Análisis de Grafos")
    print("=" * 70)
    
    # Descobrir todas las pruebas
    loader = unittest.TestLoader()
    
    # Cargar pruebas unitarias
    print("\n📋 Cargando pruebas unitarias...")
    suite_unitarias = loader.discover(
        os.path.join(project_root, 'tests', 'unit'),
        pattern='test_*.py'
    )
    
    # Cargar pruebas de integración
    print("📋 Cargando pruebas de integración...")
    suite_integracion = loader.discover(
        os.path.join(project_root, 'tests', 'integration'),
        pattern='test_*.py'
    )
    
    # Combinar todas las suites
    suite_completa = unittest.TestSuite([suite_unitarias, suite_integracion])
    
    # Configurar el runner
    stream = StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2,
        buffer=True,
        failfast=False
    )
    
    # Ejecutar pruebas
    print("🚀 Iniciando ejecución de pruebas...\n")
    inicio = time.time()
    
    resultado = runner.run(suite_completa)
    
    fin = time.time()
    tiempo_total = fin - inicio
    
    # Obtener salida detallada
    output = stream.getvalue()
    
    # Generar reporte
    print("=" * 70)
    print("REPORTE DE RESULTADOS")
    print("=" * 70)
    
    print(f"⏱️  Tiempo total: {tiempo_total:.2f} segundos")
    print(f"🧪 Pruebas ejecutadas: {resultado.testsRun}")
    print(f"✅ Pruebas exitosas: {resultado.testsRun - len(resultado.failures) - len(resultado.errors)}")
    print(f"❌ Pruebas fallidas: {len(resultado.failures)}")
    print(f"💥 Errores: {len(resultado.errors)}")
    print(f"🚫 Omitidas: {len(resultado.skipped) if hasattr(resultado, 'skipped') else 0}")
    
    # Calcular porcentaje de éxito
    if resultado.testsRun > 0:
        exito_porcentaje = ((resultado.testsRun - len(resultado.failures) - len(resultado.errors)) / resultado.testsRun) * 100
        print(f"📊 Porcentaje de éxito: {exito_porcentaje:.1f}%")
    
    print("\n" + "=" * 70)
    
    # Mostrar detalles si hay fallos
    if resultado.failures:
        print("PRUEBAS FALLIDAS:")
        print("-" * 50)
        for test, traceback in resultado.failures:
            print(f"❌ {test}")
            print(f"   {traceback.split('AssertionError:')[-1].strip()}")
        print()
    
    if resultado.errors:
        print("ERRORES EN PRUEBAS:")
        print("-" * 50)
        for test, traceback in resultado.errors:
            print(f"💥 {test}")
            print(f"   {traceback.split('Exception:')[-1].strip()}")
        print()
    
    # Mostrar salida detallada si se solicita
    if len(sys.argv) > 1 and sys.argv[1] == '--verbose':
        print("SALIDA DETALLADA:")
        print("-" * 50)
        print(output)
    
    # Determinar código de salida
    exit_code = 0 if resultado.wasSuccessful() else 1
    
    print("=" * 70)
    if resultado.wasSuccessful():
        print("🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
    else:
        print("⚠️  ALGUNAS PRUEBAS FALLARON - REVISAR RESULTADOS")
    print("=" * 70)
    
    return exit_code

def ejecutar_pruebas_unitarias():
    """Ejecuta solo las pruebas unitarias"""
    print("Ejecutando solo pruebas unitarias...\n")
    
    loader = unittest.TestLoader()
    suite = loader.discover(
        os.path.join(project_root, 'tests', 'unit'),
        pattern='test_*.py'
    )
    
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    return 0 if resultado.wasSuccessful() else 1

def ejecutar_pruebas_integracion():
    """Ejecuta solo las pruebas de integración"""
    print("Ejecutando solo pruebas de integración...\n")
    
    loader = unittest.TestLoader()
    suite = loader.discover(
        os.path.join(project_root, 'tests', 'integration'),
        pattern='test_*.py'
    )
    
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite)
    
    return 0 if resultado.wasSuccessful() else 1

def mostrar_ayuda():
    """Muestra información de uso del script"""
    print("Script de Ejecución de Pruebas - Sistema de Grafos")
    print("=" * 50)
    print("Uso:")
    print("  python run_tests.py [opción]")
    print()
    print("Opciones:")
    print("  (sin argumentos)  - Ejecutar todas las pruebas")
    print("  --unit           - Ejecutar solo pruebas unitarias")
    print("  --integration    - Ejecutar solo pruebas de integración")
    print("  --verbose        - Mostrar salida detallada")
    print("  --help           - Mostrar esta ayuda")
    print()
    print("Ejemplos:")
    print("  python run_tests.py")
    print("  python run_tests.py --unit")
    print("  python run_tests.py --verbose")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--help':
            mostrar_ayuda()
            sys.exit(0)
        elif sys.argv[1] == '--unit':
            sys.exit(ejecutar_pruebas_unitarias())
        elif sys.argv[1] == '--integration':
            sys.exit(ejecutar_pruebas_integracion())
        elif sys.argv[1] == '--verbose':
            sys.exit(ejecutar_todas_las_pruebas())
        else:
            print(f"Opción desconocida: {sys.argv[1]}")
            print("Use --help para ver opciones disponibles")
            sys.exit(1)
    else:
        sys.exit(ejecutar_todas_las_pruebas())
