import sqlite3
import json
import os

class StudentMapper:
    def __init__(self, db_path='attendance.db', mapping_file='student_mapping.json'):
        """
        Initialize the student mapper
        
        Args:
            db_path (str): Path to the face recognition SQLite database
            mapping_file (str): Path to the JSON file storing ID mappings
        """
        self.db_path = db_path
        self.mapping_file = mapping_file
        self.mappings = self.load_mappings()
    
    def load_mappings(self):
        """
        Load student ID mappings from JSON file
        
        Returns:
            dict: Dictionary mapping face recognition IDs to EduConnect IDs
        """
        if os.path.exists(self.mapping_file):
            try:
                with open(self.mapping_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading mappings: {e}")
                return {}
        return {}
    
    def save_mappings(self):
        """
        Save student ID mappings to JSON file
        """
        try:
            with open(self.mapping_file, 'w') as f:
                json.dump(self.mappings, f, indent=2)
        except Exception as e:
            print(f"Error saving mappings: {e}")
    
    def add_mapping(self, face_id, educonnect_id):
        """
        Add a mapping between face recognition ID and EduConnect ID
        
        Args:
            face_id (int): Student ID in face recognition system
            educonnect_id (str): Student ID in EduConnect system
        """
        self.mappings[str(face_id)] = educonnect_id
        self.save_mappings()
    
    def get_educonnect_id(self, face_id):
        """
        Get EduConnect ID for a face recognition ID
        
        Args:
            face_id (int): Student ID in face recognition system
            
        Returns:
            str: EduConnect ID or None if not found
        """
        return self.mappings.get(str(face_id))
    
    def remove_mapping(self, face_id):
        """
        Remove a mapping
        
        Args:
            face_id (int): Student ID in face recognition system
        """
        if str(face_id) in self.mappings:
            del self.mappings[str(face_id)]
            self.save_mappings()
    
    def get_all_mappings(self):
        """
        Get all mappings
        
        Returns:
            dict: All ID mappings
        """
        return self.mappings.copy()
    
    def get_face_students(self):
        """
        Get all students from face recognition database
        
        Returns:
            list: List of students from face recognition database
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, name, roll_number FROM students')
            students = cursor.fetchall()
            
            conn.close()
            
            # Convert to list of dictionaries
            return [{'id': row[0], 'name': row[1], 'roll_number': row[2]} for row in students]
        except Exception as e:
            print(f"Error fetching face recognition students: {e}")
            return []
    
    def create_sample_mappings(self, educonnect_students):
        """
        Create sample mappings for demonstration
        
        Args:
            educonnect_students (list): List of students from EduConnect
        """
        face_students = self.get_face_students()
        
        # Simple matching based on name (in a real scenario, this would be more sophisticated)
        for i, face_student in enumerate(face_students[:len(educonnect_students)]):
            if i < len(educonnect_students):
                educonnect_student = educonnect_students[i]
                self.add_mapping(face_student['id'], educonnect_student['_id'])

# Example usage
if __name__ == "__main__":
    mapper = StudentMapper()
    
    # Example EduConnect students (this would come from EduConnect API)
    educonnect_students = [
        {'_id': '60f7b3b3d8e5a20015f0e8a1', 'name': 'John Doe', 'email': 'john@example.com'},
        {'_id': '60f7b3b3d8e5a20015f0e8a2', 'name': 'Jane Smith', 'email': 'jane@example.com'}
    ]
    
    # Create sample mappings
    mapper.create_sample_mappings(educonnect_students)
    
    # Print all mappings
    print("Current mappings:")
    for face_id, educonnect_id in mapper.get_all_mappings().items():
        print(f"Face ID {face_id} -> EduConnect ID {educonnect_id}")