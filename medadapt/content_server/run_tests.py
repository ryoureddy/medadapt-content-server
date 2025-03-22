#!/usr/bin/env python3
"""
Comprehensive test runner for MedAdapt Content Server
Runs unit tests, integration tests, and functional tests
"""

import os
import sys
import unittest
import argparse
import logging
import time
import importlib
import test_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_run.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("medadapt_test_runner")

def run_unit_tests():
    """Run unit tests for each module"""
    logger.info("Running unit tests...")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Find and add test cases
    for module_name in ['database', 'pubmed_utils', 'bookshelf_utils', 'backup_utils']:
        try:
            # Try to import the module
            module = importlib.import_module(module_name)
            
            # Look for test_* functions in the module
            for attr_name in dir(module):
                if attr_name.startswith('test_') and callable(getattr(module, attr_name)):
                    test_suite.addTest(unittest.FunctionTestCase(getattr(module, attr_name)))
        except ImportError:
            logger.warning(f"Could not import module '{module_name}' for unit testing")
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    return result.wasSuccessful()

def run_integration_tests():
    """Run integration tests using test_server.py"""
    logger.info("Running integration tests...")
    
    return test_server.run_all_tests()

def run_performance_tests():
    """Run basic performance tests"""
    logger.info("Running performance tests...")
    
    try:
        import database
        
        # Test database performance
        start_time = time.time()
        database.initialize_database()
        init_time = time.time() - start_time
        logger.info(f"Database initialization time: {init_time:.2f} seconds")
        
        # Test resource addition performance
        start_time = time.time()
        for i in range(10):
            test_resource = {
                'id': f'perf-test-resource-{i}',
                'title': f'Performance Test Resource {i}',
                'source_type': 'test',
                'content_type': 'article',
                'cached_content': {'content': f'This is performance test resource {i}.'}
            }
            database.add_resource(test_resource)
        add_time = time.time() - start_time
        logger.info(f"Adding 10 resources time: {add_time:.2f} seconds (avg: {add_time/10:.4f}s per resource)")
        
        # Test search performance
        start_time = time.time()
        database.search_resources(query='test')
        search_time = time.time() - start_time
        logger.info(f"Search operation time: {search_time:.4f} seconds")
        
        # Determine if tests were successful based on performance thresholds
        success = (init_time < 1.0 and add_time < 2.0 and search_time < 1.0)
        if not success:
            logger.warning("Performance tests completed but exceeded recommended thresholds")
        
        return success
    except Exception as e:
        logger.error(f"Performance tests failed: {str(e)}")
        return False

def run_api_tests():
    """Run tests for external API connections"""
    logger.info("Running external API tests...")
    
    try:
        import pubmed_utils
        import bookshelf_utils
        
        pubmed_success = False
        bookshelf_success = False
        
        # Test PubMed API
        try:
            results = pubmed_utils.search_pubmed('test', 1)
            if results and len(results) > 0:
                logger.info("PubMed API connection successful")
                pubmed_success = True
            else:
                logger.warning("PubMed API returned no results")
        except Exception as e:
            logger.error(f"PubMed API test failed: {str(e)}")
        
        # Test Bookshelf API
        try:
            results = bookshelf_utils.search_bookshelf('test', 1)
            if results and len(results) > 0:
                logger.info("Bookshelf API connection successful")
                bookshelf_success = True
            else:
                logger.warning("Bookshelf API returned no results")
        except Exception as e:
            logger.error(f"Bookshelf API test failed: {str(e)}")
        
        return pubmed_success and bookshelf_success
    except Exception as e:
        logger.error(f"API tests failed: {str(e)}")
        return False

def main():
    """Run the test suite"""
    parser = argparse.ArgumentParser(description='Run MedAdapt Content Server tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--performance', action='store_true', help='Run performance tests only')
    parser.add_argument('--api', action='store_true', help='Run API tests only')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    
    args = parser.parse_args()
    
    # If no specific test type is specified, run all tests
    run_all = args.all or not (args.unit or args.integration or args.performance or args.api)
    
    # Track results
    results = {}
    
    # Run tests based on arguments
    if args.unit or run_all:
        results['unit'] = run_unit_tests()
    
    if args.integration or run_all:
        results['integration'] = run_integration_tests()
    
    if args.performance or run_all:
        results['performance'] = run_performance_tests()
    
    if args.api or run_all:
        results['api'] = run_api_tests()
    
    # Print summary
    logger.info("\n=== Test Results Summary ===")
    for test_type, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        logger.info(f"{test_type.capitalize()} Tests: {status}")
    
    # Overall status
    all_passed = all(results.values())
    logger.info(f"\nOverall Status: {'SUCCESS' if all_passed else 'FAILURE'}")
    
    # Return exit code
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 