from flask import Blueprint, request, jsonify
from models import Project, File
from extensions import db
from flask_login import login_required, current_user

projects = Blueprint('projects', __name__)

@projects.route('/', methods=['POST'])
@login_required
def create_project():
    data = request.get_json()
    name = data.get('name')
    
    new_project = Project(name=name, owner=current_user)
    db.session.add(new_project)
    db.session.commit()
    
    return jsonify({'id': new_project.id, 'name': new_project.name}), 201

@projects.route('/', methods=['GET'])
@login_required
def get_projects():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return jsonify([{'id': p.id, 'name': p.name} for p in projects])

@projects.route('/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    files = [{'id': f.id, 'name': f.name} for f in project.files]
    return jsonify({'id': project.id, 'name': project.name, 'files': files})

@projects.route('/<int:project_id>/files', methods=['POST'])
@login_required
def create_file(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    name = data.get('name')
    
    new_file = File(name=name, project=project)
    db.session.add(new_file)
    db.session.commit()
    
    return jsonify({'id': new_file.id, 'name': new_file.name}), 201

@projects.route('/files/<int:file_id>', methods=['GET'])
@login_required
def get_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.project.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403
    
    return jsonify({'id': file.id, 'name': file.name, 'content': file.content})

@projects.route('/files/<int:file_id>', methods=['PUT'])
@login_required
def update_file(file_id):
    file = File.query.get_or_404(file_id)
    if file.project.user_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403

    data = request.get_json()
    file.content = data.get('content')
    db.session.commit()
    
    return jsonify({'message': 'File updated successfully'})
