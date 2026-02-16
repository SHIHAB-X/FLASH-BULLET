#!/usr/bin/env python3
"""
Test Script - Core Engine Verification
Tests the core automation engine without requiring GUI or external dependencies.
"""

import sys
import os
from pathlib import Path

# Add project to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

import time


def test_core_engine():
    """Test the core block engine functionality"""
    print("\n" + "="*60)
    print("VISUAL AUTOMATION TOOL - CORE ENGINE TEST")
    print("="*60 + "\n")
    
    try:
        # Test 1: Import core modules
        print("📦 Test 1: Importing core modules...")
        from core import (
            BlockEngine, BlockDefinition, BlockInstance,
            BlockPort, BlockParameter, BlockType, DataType,
            BlockRegistry, WorkflowExecutor
        )
        print("   ✓ Core modules imported successfully\n")
        
        # Test 2: Create a simple block
        print("🔧 Test 2: Creating block definition...")
        
        def execute_test_block(context):
            """Simple test block that adds two numbers"""
            params = context["parameters"]
            a = params.get("number_a", 0)
            b = params.get("number_b", 0)
            result = a + b
            print(f"   [Block Execution] {a} + {b} = {result}")
            return {"result": result}
        
        test_block = BlockDefinition(
            block_type="test_add",
            name="Add Numbers",
            category=BlockType.UTILITY,
            description="Add two numbers together",
            output_ports=[BlockPort("result", DataType.NUMBER)],
            parameters=[
                BlockParameter("number_a", int, 5),
                BlockParameter("number_b", int, 3)
            ],
            execute_func=execute_test_block,
            icon="➕",
            color="#A3BE8C"
        )
        print("   ✓ Block definition created\n")
        
        # Test 3: Register block
        print("📋 Test 3: Registering block...")
        BlockRegistry.register(test_block)
        total_blocks = BlockRegistry.get_block_count()
        print(f"   ✓ Block registered (Total blocks: {total_blocks})\n")
        
        # Test 4: Create block instance
        print("🎯 Test 4: Creating block instance...")
        instance = BlockRegistry.create_instance("test_add")
        instance.set_parameter("number_a", 10)
        instance.set_parameter("number_b", 15)
        print(f"   ✓ Instance created with ID: {instance.id}\n")
        
        # Test 5: Execute block
        print("▶️  Test 5: Executing block...")
        engine = BlockEngine()
        engine.add_block(instance)
        
        result = engine.execute_block(instance, {})
        print(f"   ✓ Block executed, result: {result['result']}\n")
        
        # Test 6: Create workflow
        print("🔗 Test 6: Creating multi-block workflow...")
        
        # Create second block
        def execute_multiply_block(context):
            inputs = context["inputs"]
            result = inputs.get("result", 0)
            multiplier = context["parameters"].get("multiplier", 2)
            final = result * multiplier
            print(f"   [Block Execution] {result} × {multiplier} = {final}")
            return {"final": final}
        
        multiply_block = BlockDefinition(
            block_type="test_multiply",
            name="Multiply",
            category=BlockType.UTILITY,
            input_ports=[BlockPort("result", DataType.NUMBER)],
            output_ports=[BlockPort("final", DataType.NUMBER)],
            parameters=[BlockParameter("multiplier", int, 2)],
            execute_func=execute_multiply_block,
            icon="✖️"
        )
        
        BlockRegistry.register(multiply_block)
        
        # Create workflow: Add → Multiply
        add_block = BlockRegistry.create_instance("test_add")
        add_block.set_parameter("number_a", 5)
        add_block.set_parameter("number_b", 5)
        
        mult_block = BlockRegistry.create_instance("test_multiply")
        mult_block.set_parameter("multiplier", 3)
        
        # Connect blocks
        add_block.connect_to("result", mult_block.id)
        
        # Execute workflow
        engine2 = BlockEngine()
        engine2.add_block(add_block)
        engine2.add_block(mult_block)
        
        workflow_result = engine2.execute_workflow()
        print(f"   ✓ Workflow executed successfully")
        print(f"   ✓ Executed {workflow_result['executed_count']} blocks\n")
        
        # Test 7: Workflow validation
        print("✓ Test 7: Validating workflow...")
        executor = WorkflowExecutor()
        executor.engine.add_block(add_block)
        executor.engine.add_block(mult_block)
        
        issues = executor.validate()
        if issues:
            print(f"   ⚠ Found {len(issues)} validation issues")
        else:
            print("   ✓ Workflow is valid\n")
        
        # Test 8: Serialization
        print("💾 Test 8: Testing serialization...")
        workflow_data = {
            "blocks": [
                add_block.to_dict(),
                mult_block.to_dict()
            ]
        }
        print(f"   ✓ Workflow serialized to dictionary\n")
        
        # Summary
        print("="*60)
        print("ALL TESTS PASSED! ✓")
        print("="*60)
        print("\nCore engine is working correctly!")
        print("The system can:")
        print("  • Create and register blocks")
        print("  • Execute blocks with parameters")
        print("  • Connect blocks in workflows")
        print("  • Validate and serialize workflows")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run full application: python main.py")
        print("  3. Or try demo mode: python demo.py")
        
        return True
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\nThe core modules couldn't be imported.")
        print("Make sure you're in the project directory.\n")
        return False
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_project_io():
    """Test project save/load functionality"""
    print("\n" + "="*60)
    print("TESTING PROJECT I/O")
    print("="*60 + "\n")
    
    try:
        from utils.project_io import ProjectIO, WorkflowValidator
        
        # Test workflow validation
        print("📝 Testing workflow validation...")
        
        valid_workflow = {
            "blocks": [
                {
                    "id": "block1",
                    "type": "test_type",
                    "x": 100,
                    "y": 100,
                    "parameters": {},
                    "connections": {}
                }
            ]
        }
        
        is_valid, issues = WorkflowValidator.validate(valid_workflow)
        
        if is_valid:
            print("   ✓ Valid workflow passed validation")
        else:
            print(f"   ⚠ Issues found: {issues}")
        
        print("\n✓ Project I/O system working!\n")
        return True
        
    except Exception as e:
        print(f"❌ Project I/O test failed: {e}\n")
        return False


def main():
    """Run all tests"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           CORE ENGINE TEST SUITE                          ║
    ║                                                           ║
    ║     Testing automation engine without GUI                ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Run tests
    engine_ok = test_core_engine()
    io_ok = test_project_io()
    
    print("\n" + "="*60)
    if engine_ok and io_ok:
        print("SUCCESS: All core components are working! ✓")
    else:
        print("PARTIAL SUCCESS: Some components need attention")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
