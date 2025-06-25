from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# In-memory storage
students = {}
classes = {}
registrations = {}  # class_id -> [student_ids]

# 1. Create Student
@app.route('/students', methods=['POST'])
def create_student():
    data = request.json
    student_id = str(uuid.uuid4())
    students[student_id] = {
        'id': student_id,
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'middle_name': data.get('middle_name', ''),
        'age': data['age'],
        'city': data['city']
    }
    return jsonify(students[student_id]), 201

# 2. Update Student
@app.route('/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    if student_id not in students:
        return jsonify({'error': 'Student not found'}), 404
    
    data = request.json
    for key in ['first_name', 'last_name', 'middle_name', 'age', 'city']:
        if key in data:
            students[student_id][key] = data[key]
    
    return jsonify(students[student_id])

# 3. Delete Student
@app.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    if student_id not in students:
        return jsonify({'error': 'Student not found'}), 404
    
    # Remove from all classes
    for class_id in registrations:
        if student_id in registrations[class_id]:
            registrations[class_id].remove(student_id)
    
    deleted = students.pop(student_id)
    return jsonify({'message': 'Student deleted', 'student': deleted})

# 4. Create Class
@app.route('/classes', methods=['POST'])
def create_class():
    data = request.json
    class_id = str(uuid.uuid4())
    classes[class_id] = {
        'id': class_id,
        'class_name': data['class_name'],
        'description': data['description'],
        'start_date': data['start_date'],
        'end_date': data['end_date'],
        'number_of_hours': data['number_of_hours']
    }
    registrations[class_id] = []
    return jsonify(classes[class_id]), 201

# 5. Update Class
@app.route('/classes/<class_id>', methods=['PUT'])
def update_class(class_id):
    if class_id not in classes:
        return jsonify({'error': 'Class not found'}), 404
    
    data = request.json
    for key in ['class_name', 'description', 'start_date', 'end_date', 'number_of_hours']:
        if key in data:
            classes[class_id][key] = data[key]
    
    return jsonify(classes[class_id])

# 6. Delete Class
@app.route('/classes/<class_id>', methods=['DELETE'])
def delete_class(class_id):
    if class_id not in classes:
        return jsonify({'error': 'Class not found'}), 404
    
    deleted = classes.pop(class_id)
    registrations.pop(class_id, None)
    return jsonify({'message': 'Class deleted', 'class': deleted})

# 7. Register Student to Class
@app.route('/classes/<class_id>/register', methods=['POST'])
def register_student(class_id):
    if class_id not in classes:
        return jsonify({'error': 'Class not found'}), 404
    
    student_id = request.json['student_id']
    if student_id not in students:
        return jsonify({'error': 'Student not found'}), 404
    
    if student_id in registrations[class_id]:
        return jsonify({'error': 'Already registered'}), 400
    
    registrations[class_id].append(student_id)
    return jsonify({
        'message': 'Registered successfully',
        'class': classes[class_id],
        'student': students[student_id]
    }), 201

# 8. Get Students in Class
@app.route('/classes/<class_id>/students', methods=['GET'])
def get_class_students(class_id):
    if class_id not in classes:
        return jsonify({'error': 'Class not found'}), 404
    
    student_list = [students[sid] for sid in registrations[class_id] if sid in students]
    return jsonify({
        'class': classes[class_id],
        'students': student_list,
        'total': len(student_list)
    })

# Helper endpoints
@app.route('/students', methods=['GET'])
def get_all_students():
    return jsonify(list(students.values()))

@app.route('/classes', methods=['GET'])
def get_all_classes():
    return jsonify(list(classes.values()))

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'students': len(students), 'classes': len(classes)})

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Student Management API',
        'endpoints': {
            'POST /students': 'Create student',
            'PUT /students/<id>': 'Update student', 
            'DELETE /students/<id>': 'Delete student',
            'POST /classes': 'Create class',
            'PUT /classes/<id>': 'Update class',
            'DELETE /classes/<id>': 'Delete class',
            'POST /classes/<id>/register': 'Register student',
            'GET /classes/<id>/students': 'Get class students'
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)