# CGPA Calculator Backend
# Flask API for CGPA calculation with comprehensive modules

from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# ----------------------------
# Input Module
# ----------------------------
def get_console_input():
    """Console-based input for standalone usage"""
    semesters = int(input("Enter number of semesters: "))
    all_semesters = []

    for sem in range(1, semesters + 1):
        print(f"\n--- Semester {sem} ---")
        subjects = int(input("Enter number of subjects: "))
        sem_data = []
        for sub in range(1, subjects + 1):
            gp = float(input(f"Enter Grade Point for subject {sub}: "))
            cr = float(input(f"Enter Credit for subject {sub}: "))
            sem_data.append({"gp": gp, "credits": cr})
        all_semesters.append({"subjects": sem_data})
    return {"semesters": all_semesters}

def parse_api_input(data):
    """Parse JSON input from API request"""
    if not isinstance(data, dict) or "semesters" not in data:
        raise ValueError("Invalid input format. Expected JSON with 'semesters' key.")
    
    if not isinstance(data["semesters"], list) or len(data["semesters"]) == 0:
        raise ValueError("Semesters must be a non-empty list.")
    
    return data

# ----------------------------
# Validation Module
# ----------------------------
def validate_data(data):
    """Comprehensive data validation"""
    semesters = data["semesters"]
    
    for sem_i, sem in enumerate(semesters, start=1):
        if "subjects" not in sem or not isinstance(sem["subjects"], list):
            raise ValueError(f"Semester {sem_i}: Missing or invalid 'subjects' field")
        
        if len(sem["subjects"]) == 0:
            raise ValueError(f"Semester {sem_i} has no subjects!")
        
        for sub_i, subject in enumerate(sem["subjects"], start=1):
            if not isinstance(subject, dict):
                raise ValueError(f"Semester {sem_i}, Subject {sub_i}: Subject must be an object")
            
            if "gp" not in subject or "credits" not in subject:
                raise ValueError(f"Semester {sem_i}, Subject {sub_i}: Missing 'gp' or 'credits' field")
            
            try:
                gp = float(subject["gp"])
                cr = float(subject["credits"])
            except (ValueError, TypeError):
                raise ValueError(f"Semester {sem_i}, Subject {sub_i}: GP and Credits must be numbers")
            
            if gp < 0 or gp > 10:
                raise ValueError(f"Semester {sem_i}, Subject {sub_i}: GP must be between 0-10, got {gp}")
            
            if cr <= 0:
                raise ValueError(f"Semester {sem_i}, Subject {sub_i}: Credits must be positive, got {cr}")

# ----------------------------
# Calculation Module
# ----------------------------
def calculate_sgpa(subjects):
    """Calculate SGPA for a semester"""
    total_points = sum(subject["gp"] * subject["credits"] for subject in subjects)
    total_credits = sum(subject["credits"] for subject in subjects)
    return round(total_points / total_credits, 2), total_credits

def calculate_cgpa(sgpas):
    """Calculate CGPA from list of SGPAs"""
    return round(sum(sgpas) / len(sgpas), 2)

def process_calculation(data):
    """Main calculation processing"""
    semesters = data["semesters"]
    sgpas = []
    semester_details = []
    
    for i, sem in enumerate(semesters, start=1):
        subjects = sem["subjects"]
        sgpa, total_credits = calculate_sgpa(subjects)
        sgpas.append(sgpa)
        semester_details.append({
            "semester": i,
            "sgpa": sgpa,
            "total_credits": total_credits,
            "subject_count": len(subjects)
        })
    
    cgpa = calculate_cgpa(sgpas)
    
    return {
        "sgpas": sgpas,
        "cgpa": cgpa,
        "total_semesters": len(sgpas),
        "semester_details": semester_details
    }

# ----------------------------
# Result Module
# ----------------------------
def show_console_results(result):
    """Display results in console format"""
    print("\n" + "="*50)
    print("           CGPA CALCULATION RESULTS")
    print("="*50)
    
    for detail in result["semester_details"]:
        print(f"Semester {detail['semester']:2d} | SGPA: {detail['sgpa']:5.2f} | Credits: {detail['total_credits']:4.1f} | Subjects: {detail['subject_count']}")
    
    print("-"*50)
    print(f"Final CGPA: {result['cgpa']:.2f} ({result['total_semesters']} semesters)")
    print("="*50)

def format_api_response(result, status="success"):
    """Format response for API"""
    return {
        "status": status,
        "data": result,
        "message": f"CGPA calculated successfully for {result['total_semesters']} semesters"
    }

# ----------------------------
# Flask API Routes
# ----------------------------
@app.route('/api/calculate', methods=['POST'])
def calculate_cgpa_api():
    """Main API endpoint for CGPA calculation"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        # Parse and validate input
        parsed_data = parse_api_input(data)
        validate_data(parsed_data)
        
        # Calculate CGPA
        result = process_calculation(parsed_data)
        
        # Return formatted response
        return jsonify(format_api_response(result))
        
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "CGPA Calculator API is running",
        "version": "1.0.0"
    })

@app.route('/api/sample', methods=['GET'])
def get_sample_data():
    """Get sample input data format"""
    sample_data = {
        "semesters": [
            {
                "subjects": [
                    {"gp": 9.0, "credits": 3.0},
                    {"gp": 8.5, "credits": 4.0},
                    {"gp": 9.2, "credits": 3.0}
                ]
            },
            {
                "subjects": [
                    {"gp": 8.8, "credits": 4.0},
                    {"gp": 9.1, "credits": 3.0},
                    {"gp": 8.7, "credits": 3.0}
                ]
            }
        ]
    }
    
    return jsonify({
        "status": "success",
        "sample_input": sample_data,
        "description": "Sample input format for CGPA calculation"
    })

# ----------------------------
# Main Program (Console Mode)
# ----------------------------
def run_console_mode():
    """Run calculator in console mode"""
    print("🎓 CGPA Calculator - Console Mode")
    print("="*40)
    
    try:
        # Get input
        data = get_console_input()
        
        # Validate
        validate_data(data)
        
        # Calculate
        result = process_calculation(data)
        
        # Show results
        show_console_results(result)
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "console":
        # Run in console mode
        run_console_mode()
    else:
        # Run Flask API server
        print("🚀 Starting CGPA Calculator API Server...")
        print("📍 API Endpoints:")
        print("   POST /api/calculate - Calculate CGPA")
        print("   GET  /api/health   - Health check")
        print("   GET  /api/sample   - Get sample data format")
        print("\n🌐 Server running on http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)

# ----------------------------
# Usage Examples
# ----------------------------
"""
USAGE EXAMPLES:

1. Console Mode:
   python cgpa_calculator.py console

2. API Server Mode:
   python cgpa_calculator.py

3. API Usage (POST to /api/calculate):
   {
     "semesters": [
       {
         "subjects": [
           {"gp": 9.0, "credits": 3.0},
           {"gp": 8.5, "credits": 4.0}
         ]
       },
       {
         "subjects": [
           {"gp": 9.2, "credits": 3.0},
           {"gp": 8.8, "credits": 4.0}
         ]
       }
     ]
   }

4. Frontend Integration:
   The HTML frontend can call the API using fetch():
   
   fetch('http://localhost:5000/api/calculate', {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
     },
     body: JSON.stringify(data)
   })
   .then(response => response.json())
   .then(result => console.log(result));
"""