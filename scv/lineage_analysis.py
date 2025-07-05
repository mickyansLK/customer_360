#!/usr/bin/env python3
"""
SCV Project dbt Lineage Analysis
This script analyzes the dbt project lineage and generates insights
"""

import json
import os
import sys
from pathlib import Path

def load_manifest():
    """Load dbt manifest.json file"""
    manifest_path = Path("target/manifest.json")
    if not manifest_path.exists():
        print("Error: manifest.json not found. Run 'dbt compile' first.")
        sys.exit(1)
    
    with open(manifest_path, 'r') as f:
        return json.load(f)

def analyze_lineage(manifest):
    """Analyze the dbt project lineage"""
    
    # Extract models and their dependencies
    models = manifest.get('nodes', {})
    sources = manifest.get('sources', {})
    
    print("=" * 80)
    print("SCV PROJECT DBT LINEAGE ANALYSIS")
    print("=" * 80)
    
    # Analyze sources
    print("\n📊 DATA SOURCES:")
    print("-" * 40)
    for source_key, source_info in sources.items():
        if source_info.get('resource_type') == 'source':
            print(f"• {source_info['name']} ({source_info['source_name']})")
            print(f"  - Database: {source_info.get('database', 'N/A')}")
            print(f"  - Schema: {source_info.get('schema', 'N/A')}")
            print(f"  - Tables: {len(source_info.get('tables', []))}")
    
    # Analyze models by layer
    bronze_models = []
    silver_models = []
    gold_models = []
    
    for model_key, model_info in models.items():
        if model_info.get('resource_type') == 'model':
            model_name = model_info['name']
            if model_name.startswith('bronze'):
                bronze_models.append(model_info)
            elif model_name.startswith('silver'):
                silver_models.append(model_info)
            elif model_name.startswith('gold'):
                gold_models.append(model_info)
    
    print(f"\n🏗️  BRONZE LAYER ({len(bronze_models)} models):")
    print("-" * 40)
    for model in bronze_models:
        print(f"• {model['name']}")
        print(f"  - Materialization: {model.get('config', {}).get('materialized', 'view')}")
        print(f"  - Dependencies: {len(model.get('depends_on', {}).get('nodes', []))}")
    
    print(f"\n⚡ SILVER LAYER ({len(silver_models)} models):")
    print("-" * 40)
    for model in silver_models:
        print(f"• {model['name']}")
        print(f"  - Materialization: {model.get('config', {}).get('materialized', 'view')}")
        deps = model.get('depends_on', {}).get('nodes', [])
        print(f"  - Dependencies: {len(deps)}")
        for dep in deps:
            if 'model.' in dep:
                dep_name = dep.split('.')[-1]
                print(f"    └─ {dep_name}")
    
    print(f"\n🎯 GOLD LAYER ({len(gold_models)} models):")
    print("-" * 40)
    for model in gold_models:
        print(f"• {model['name']}")
        print(f"  - Materialization: {model.get('config', {}).get('materialized', 'view')}")
        deps = model.get('depends_on', {}).get('nodes', [])
        print(f"  - Dependencies: {len(deps)}")
        for dep in deps:
            if 'model.' in dep:
                dep_name = dep.split('.')[-1]
                print(f"    └─ {dep_name}")
    
    # Analyze data flow
    print(f"\n🔄 DATA FLOW ANALYSIS:")
    print("-" * 40)
    
    # Find the gold model and trace its lineage
    if gold_models:
        gold_model = gold_models[0]
        print(f"Gold Model: {gold_model['name']}")
        
        def trace_lineage(model_key, level=0):
            model_info = models.get(model_key)
            if not model_info:
                return
            
            indent = "  " * level
            print(f"{indent}└─ {model_info['name']} ({model_info.get('config', {}).get('materialized', 'view')})")
            
            deps = model_info.get('depends_on', {}).get('nodes', [])
            for dep in deps:
                if 'model.' in dep:
                    trace_lineage(dep, level + 1)
        
        deps = gold_model.get('depends_on', {}).get('nodes', [])
        for dep in deps:
            if 'model.' in dep:
                trace_lineage(dep, 1)
    
    # Performance analysis
    print(f"\n⚡ PERFORMANCE METRICS:")
    print("-" * 40)
    
    total_models = len(bronze_models) + len(silver_models) + len(gold_models)
    print(f"Total Models: {total_models}")
    print(f"Bronze Models: {len(bronze_models)} (Views)")
    print(f"Silver Models: {len(silver_models)} (Tables)")
    print(f"Gold Models: {len(gold_models)} (Tables)")
    
    # Calculate complexity
    max_deps = 0
    for model in models.values():
        if model.get('resource_type') == 'model':
            deps = len(model.get('depends_on', {}).get('nodes', []))
            max_deps = max(max_deps, deps)
    
    print(f"Maximum Dependencies: {max_deps}")
    
    # Data quality coverage
    tests = [node for node in models.values() if node.get('resource_type') == 'test']
    print(f"Data Quality Tests: {len(tests)}")

def generate_dependency_matrix(manifest):
    """Generate a dependency matrix for the models"""
    
    models = manifest.get('nodes', {})
    
    print(f"\n📋 DEPENDENCY MATRIX:")
    print("-" * 80)
    
    # Get all model names
    model_names = []
    for model_key, model_info in models.items():
        if model_info.get('resource_type') == 'model':
            model_names.append(model_info['name'])
    
    model_names.sort()
    
    # Print header
    print(f"{'Model':<25}", end="")
    for dep in model_names:
        print(f"{dep[:8]:<10}", end="")
    print()
    print("-" * (25 + len(model_names) * 10))
    
    # Print matrix
    for model_name in model_names:
        print(f"{model_name:<25}", end="")
        
        # Find the model info
        model_info = None
        for model_key, info in models.items():
            if info.get('resource_type') == 'model' and info['name'] == model_name:
                model_info = info
                break
        
        if model_info:
            deps = model_info.get('depends_on', {}).get('nodes', [])
            for dep_name in model_names:
                has_dep = any(dep_name in dep for dep in deps)
                print(f"{'✓' if has_dep else ' ':>9}", end="")
        print()

def main():
    """Main function"""
    try:
        manifest = load_manifest()
        analyze_lineage(manifest)
        generate_dependency_matrix(manifest)
        
        print(f"\n✅ Lineage analysis completed!")
        print(f"📊 Generated files:")
        print(f"   • scv_lineage_graph.svg - Visual lineage graph")
        print(f"   • dbt docs available at http://localhost:8081")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 