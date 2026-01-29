from flask import Blueprint, request, jsonify, render_template
from datetime import datetime

from app import db
from app.models import (
    Event,
    Workout,
    Exercise,
    Note,
    DailyStatus,
    Message
)

main = Blueprint('main', __name__)

@main.route('/app')
def app_view():
    return render_template('index.html')


@main.route('/events', methods=['POST'])
def create_event():
    data = request.json

    event = Event(
        title=data['title'],
        description=data.get('description'),
        event_type=data.get('event_type'),
        subject=data.get('subject'),
        event_date=datetime.strptime(data['event_date'], '%Y-%m-%d').date(),
        email_reminder=data.get('email_reminder', False)
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({'message': 'Evento creado'}), 201

@main.route('/events', methods=['GET'])
def get_events():
    events = Event.query.all()
    return jsonify([
        {
            'id': e.id,
            'title': e.title,
            'date': e.event_date.isoformat(),
            'completed': e.completed
        } for e in events
    ])

@main.route('/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    event = Event.query.get_or_404(event_id)
    data = request.json

    event.title = data.get('title', event.title)
    event.completed = data.get('completed', event.completed)

    db.session.commit()
    return jsonify({'message': 'Evento actualizado'})

@main.route('/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Evento eliminado'})


@main.route('/workouts', methods=['POST'])
def create_workout():
    data = request.json

    workout = Workout(
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        routine=data.get('routine'),
        notes=data.get('notes')
    )

    db.session.add(workout)
    db.session.commit()

    return jsonify({'id': workout.id}), 201


@main.route('/workouts/<int:workout_id>/exercises', methods=['POST'])
def add_exercise(workout_id):
    data = request.json

    exercise = Exercise(
        workout_id=workout_id,
        name=data['name'],
        sets=data.get('sets'),
        reps=data.get('reps'),
        weight=data.get('weight')
    )

    db.session.add(exercise)
    db.session.commit()

    return jsonify({'message': 'Ejercicio agregado'}), 201


@main.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.all()
    return jsonify([
        {
            'id': w.id,
            'date': w.date.isoformat(),
            'routine': w.routine
        } for w in workouts
    ])


@main.route('/notes', methods=['POST'])
def create_note():
    data = request.json
    note = Note(content=data['content'])
    db.session.add(note)
    db.session.commit()
    return jsonify({'message': 'Nota creada'}), 201


@main.route('/notes', methods=['GET'])
def get_notes():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return jsonify([
        {'id': n.id, 'content': n.content}
        for n in notes
    ])


@main.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': 'Nota eliminada'})


@main.route('/status', methods=['POST'])
def set_daily_status():
    data = request.json

    status = DailyStatus(
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        mood=data.get('mood'),
        note=data.get('note')
    )

    db.session.add(status)
    db.session.commit()
    return jsonify({'message': 'Estado guardado'}), 201


@main.route('/status', methods=['GET'])
def get_daily_status():
    statuses = DailyStatus.query.all()
    return jsonify([
        {
            'date': s.date.isoformat(),
            'mood': s.mood,
            'note': s.note
        } for s in statuses
    ])

@main.route('/message', methods=['POST'])
def set_message():
    data = request.json

    Message.query.update({'active': False})

    msg = Message(content=data['content'])
    db.session.add(msg)
    db.session.commit()

    return jsonify({'message': 'Mensaje actualizado'})

@main.route('/message', methods=['GET'])
def get_message():
    msg = Message.query.filter_by(active=True).first()
    return jsonify({'message': msg.content if msg else ''})
