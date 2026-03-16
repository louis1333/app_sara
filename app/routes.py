from flask import Blueprint, request, jsonify, render_template
from datetime import datetime, timedelta
from app.email import send_email
from app import db
from app.models import (
    Event,
    Workout,
    Exercise,
    ExerciseSet,
    Note,
    DailyStatus,
    Message
)

main = Blueprint('main', __name__)

# =====================================================
# KEEP-ALIVE
# =====================================================

@main.route('/ping')
def ping():
    return jsonify({'status': 'ok'}), 200


# =====================================================
# ENTRY POINT
# =====================================================

@main.route('/')
def index():
    """
    Página de entrada.
    Puede ser landing simple o redirección.
    """
    return render_template('index.html')


# =====================================================
# VISTAS APP WEB (FRONTEND)
# =====================================================

@main.route('/app')
def app_home():
    return render_template('home.html')


@main.route('/app/events')
def app_events():
    return render_template('events.html')


@main.route('/app/workouts')
def app_workouts():
    return render_template('workouts.html')


@main.route('/app/notes')
def app_notes():
    return render_template('notes.html')


# =====================================================
# EVENTOS / CALENDARIO (API)
# =====================================================

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
    events = Event.query.order_by(Event.event_date.asc()).all()
    return jsonify([
        {
            'id': e.id,
            'title': e.title,
            'date': e.event_date.isoformat(),
            'completed': e.completed
        } for e in events
    ])


@main.route('/events/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get_or_404(event_id)
    return jsonify({
        'id': event.id,
        'title': event.title,
        'description': event.description,
        'date': event.event_date.isoformat(),
        'completed': event.completed
    })


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

# =====================================================
# WORKOUTS / GIMNASIO (API)
# =====================================================

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


@main.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.order_by(Workout.date.desc()).all()
    return jsonify([
        {
            'id': w.id,
            'date': w.date.isoformat(),
            'routine': w.routine
        } for w in workouts
    ])


# =====================================================
# EJERCICIOS
# =====================================================

@main.route('/workouts/<int:workout_id>', methods=['DELETE'])
def delete_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    db.session.delete(workout)
    db.session.commit()
    return jsonify({'message': 'Rutina eliminada'})


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
    db.session.flush()

    sets_count = data.get('sets', 0)
    if sets_count:
        for i in range(1, int(sets_count) + 1):
            db.session.add(ExerciseSet(exercise_id=exercise.id, set_number=i))

    db.session.commit()
    return jsonify({'id': exercise.id, 'message': 'Ejercicio agregado'}), 201


@main.route('/workouts/<int:workout_id>/exercises', methods=['GET'])
def get_exercises(workout_id):
    exercises = Exercise.query.filter_by(workout_id=workout_id).all()
    result = []
    for e in exercises:
        sets_data = ExerciseSet.query.filter_by(exercise_id=e.id).order_by(ExerciseSet.set_number).all()
        result.append({
            'id': e.id,
            'name': e.name,
            'sets': e.sets,
            'reps': e.reps,
            'weight': e.weight,
            'sets_data': [{'set_number': s.set_number, 'reps': s.reps, 'weight': s.weight} for s in sets_data]
        })
    return jsonify(result)


@main.route('/exercises/<int:exercise_id>/sets', methods=['PUT'])
def save_exercise_sets(exercise_id):
    Exercise.query.get_or_404(exercise_id)
    data = request.json
    ExerciseSet.query.filter_by(exercise_id=exercise_id).delete()
    for s in data:
        db.session.add(ExerciseSet(
            exercise_id=exercise_id,
            set_number=s['set_number'],
            reps=s.get('reps'),
            weight=s.get('weight')
        ))
    db.session.commit()
    return jsonify({'message': 'Sets guardados'})


@main.route('/exercises/<int:exercise_id>', methods=['DELETE'])
def delete_exercise(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    db.session.delete(exercise)
    db.session.commit()
    return jsonify({'message': 'Ejercicio eliminado'})

@main.route('/exercises/<int:exercise_id>', methods=['PUT'])
def update_exercise(exercise_id):
    exercise = Exercise.query.get_or_404(exercise_id)
    data = request.json

    exercise.name = data.get('name', exercise.name)
    exercise.sets = data.get('sets', exercise.sets)
    exercise.reps = data.get('reps', exercise.reps)
    exercise.weight = data.get('weight', exercise.weight)

    db.session.commit()

    return jsonify({'message': 'Ejercicio actualizado'}), 200

# =====================================================
# NOTAS (API)
# =====================================================

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
        {
            'id': n.id,
            'content': n.content
        } for n in notes
    ])


@main.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()

    return jsonify({'message': 'Nota eliminada'})


# =====================================================
# ESTADO DEL DÍA (API)
# =====================================================

@main.route('/status', methods=['POST'])
def set_daily_status():
    data = request.json
    date = datetime.strptime(data['date'], '%Y-%m-%d').date()

    # Un solo estado por día
    DailyStatus.query.filter_by(date=date).delete()

    status = DailyStatus(
        date=date,
        mood=data.get('mood'),
        note=data.get('note')
    )

    db.session.add(status)
    db.session.commit()
    send_email("Estado del dia: "+status.mood, "mensaje: "+status.note, "louis.alejo133@gmail.com")
    return jsonify({'message': 'Estado guardado'}), 201


@main.route('/status', methods=['GET'])
def get_daily_status():
    statuses = DailyStatus.query.order_by(DailyStatus.date.desc()).all()
    return jsonify([
        {
            'date': s.date.isoformat(),
            'mood': s.mood,
            'note': s.note
        } for s in statuses
    ])


# =====================================================
# MENSAJE DIARIO (API)
# =====================================================

@main.route('/message', methods=['POST'])
def set_message():
    data = request.json

    Message.query.update({'active': False})

    msg = Message(content=data['content'], active=True)
    db.session.add(msg)
    db.session.commit()

    return jsonify({'message': 'Mensaje actualizado'})


@main.route('/message', methods=['GET'])
def get_message():
    msg = Message.query.filter_by(active=True).first()
    return jsonify({'message': msg.content if msg else ''})


# =====================================================
# RECORDATORIOS DE EVENTOS (API)
# =====================================================

@main.route('/send-reminders', methods=['GET'])
def send_reminders():
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)

    events_today = Event.query.filter_by(event_date=today, completed=False).order_by(Event.event_time).all()
    events_tomorrow = Event.query.filter_by(event_date=tomorrow, completed=False).order_by(Event.event_time).all()

    if not events_today and not events_tomorrow:
        return jsonify({'message': 'Sin eventos para notificar'}), 200

    def format_event(e):
        time_str = e.event_time.strftime('%H:%M') if e.event_time else ''
        type_labels = {'exam': '📝 Examen', 'task': '✅ Tarea', 'reminder': '🔔 Recordatorio'}
        tipo = type_labels.get(e.event_type, '📌 Evento')
        parts = [f"<li style='margin-bottom:8px'><strong>{tipo}: {e.title}</strong>"]
        if time_str:
            parts.append(f" — {time_str}")
        if e.subject:
            parts.append(f"<br><span style='color:#666'>Materia: {e.subject}</span>")
        if e.description:
            parts.append(f"<br><span style='color:#666'>{e.description}</span>")
        parts.append("</li>")
        return ''.join(parts)

    sections = []

    if events_today:
        items = ''.join(format_event(e) for e in events_today)
        sections.append(f"""
            <h2 style='color:#e879a0;margin-bottom:8px'>📅 Hoy — {today.strftime('%d de %B')}</h2>
            <ul style='padding-left:16px;margin-bottom:24px'>{items}</ul>
        """)

    if events_tomorrow:
        items = ''.join(format_event(e) for e in events_tomorrow)
        sections.append(f"""
            <h2 style='color:#f0a0c0;margin-bottom:8px'>🗓 Mañana — {tomorrow.strftime('%d de %B')}</h2>
            <ul style='padding-left:16px;margin-bottom:24px'>{items}</ul>
        """)

    html_body = f"""
        <div style='font-family:sans-serif;max-width:480px;margin:auto;padding:24px;background:#fdf2f8;border-radius:16px'>
            <h1 style='color:#e879a0;margin-bottom:4px'>🌸 Recordatorio para mi koalita</h1>
            <p style='color:#888;margin-bottom:24px'>Aquí tienes tus eventos próximos 💕</p>
            {''.join(sections)}
            <p style='color:#aaa;font-size:12px;margin-top:16px'>Con amor 💗</p>
        </div>
    """

    send_email("Recordatorio evento", html_body, "saradanielaayalam@gmail.com")
    return jsonify({'message': 'Recordatorio enviado', 'hoy': len(events_today), 'mañana': len(events_tomorrow)}), 200
