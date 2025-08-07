# Automated Testing Implementation

## Overview

This document describes the automated testing system added to the CD-Test pipeline. The testing system compares application output against reference data and generates binary results (1/0) for each test case.

## Pipeline Integration

The automated testing step has been integrated into the CD-Test pipeline (`.github/workflows/cd_test.yml`) and runs **before** Docker image building. The pipeline will only proceed to build and push Docker images if all tests pass.

### Pipeline Flow
```
1. Checkout code
2. Set up Python environment
3. Install Poetry dependencies
4. 🔥 RUN AUTOMATED TESTS 🔥
5. Upload test results as artifacts
6. (Only if tests pass) Build Docker image
7. (Only if tests pass) Push to registry
8. (Only if tests pass) Create git tag
```

## Test Data Structure

### Input Data (`test_data/input_data.json`)
Contains test cases with different HTTP endpoints to test application behavior:
- GitHub API (should return success)
- HTTP 200 endpoint (should return success) 
- HTTP 404 endpoint (should return failure)
- HTTP 500 endpoint (should return failure)
- Connection timeout (should return failure)

### Reference Data (`test_data/reference_data.json`)
Contains expected results for each test case:
- Expected application output
- Pass/fail criteria
- Test descriptions

## Test Script (`scripts/run_automated_tests.py`)

### Functionality
- Loads test data and reference data from JSON files
- Executes the application (`fetch_greeting()`) with each test endpoint
- Compares actual output with expected output
- Generates binary results (1 = pass, 0 = fail)
- Saves results to files
- Exits with code 0 (success) or 1 (failure)

### Output Files
- `test_results/binary_results.txt` - One binary result per line (main requirement)
- `test_results/detailed_results.json` - Detailed test information for debugging

### Example Output
```
Binary results: [1, 1, 1, 1, 1]
✅ ALL TESTS PASSED - Pipeline can proceed
```

## Application Modifications

### Enhanced `fetch_greeting()` Function
- Added optional `url` parameter for testing different endpoints
- Added proper exception handling for network errors
- Added 5-second timeout for faster test execution
- Maintains backward compatibility (default URL still works)

### Updated Unit Tests
- Modified existing tests to work with new function signature
- Added test for custom URL functionality

## Pipeline Behavior

### ✅ When Tests Pass
- All tests return binary result `1`
- Script exits with code 0
- Pipeline continues to Docker build and registry push
- Test results uploaded as GitHub Actions artifacts

### ❌ When Tests Fail
- One or more tests return binary result `0`
- Script exits with code 1
- **Pipeline is blocked** - Docker build does not run
- Test results still uploaded for debugging
- Pipeline fails with clear error message

## Test Cases

| Test ID | Endpoint | Expected Result | Purpose |
|---------|----------|-----------------|---------|
| 1 | https://api.github.com | Success greeting | Normal operation |
| 2 | https://httpbin.org/status/200 | Success greeting | HTTP 200 handling |
| 3 | https://httpbin.org/status/404 | Failure message | HTTP 404 handling |
| 4 | https://httpbin.org/status/500 | Failure message | HTTP 500 handling |
| 5 | http://192.0.2.1:12345/nonexistent | Failure message | Network timeout handling |

## Running Tests Locally

```bash
# Install dependencies
poetry install --no-root

# Run automated tests
poetry run python scripts/run_automated_tests.py

# Check results
cat test_results/binary_results.txt
```

## Files Added/Modified

### New Files
- `test_data/input_data.json` - Test input data
- `test_data/reference_data.json` - Expected results
- `scripts/run_automated_tests.py` - Test automation script
- `test_results/` - Generated test output directory
- `.gitignore` - Excludes generated test results
- `AUTOMATED_TESTING.md` - This documentation

### Modified Files
- `.github/workflows/cd_test.yml` - Added testing steps
- `app.py` - Enhanced fetch_greeting() function
- `tests/test_app.py` - Updated unit tests

## Quality Gates

The automated testing system ensures:
1. **Application functionality** is verified before deployment
2. **Binary pass/fail results** are generated as required
3. **Pipeline blocking** prevents bad code from reaching Docker registry
4. **Complete traceability** through detailed test results
5. **Fast feedback** with 5-second timeouts and parallel execution

This implementation successfully meets all requirements:
- ✅ Fixed test data and reference data in repository
- ✅ Script compares test vs reference data with current app version
- ✅ Output file contains binary (1/0) per data entry
- ✅ Tests run before Docker setup
- ✅ Pipeline blocked if tests fail 