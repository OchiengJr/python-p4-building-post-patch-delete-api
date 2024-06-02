from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError

from models import db, User, Review, Game

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def index():
    return "Index for Game/Review/User API"


@app.route('/games')
def games():
    try:
        games = [game.to_dict() for game in Game.query.all()]
        return jsonify(games), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500


@app.route('/games/<int:id>')
def game_by_id(id):
    try:
        game = Game.query.get(id)
        if game:
            return jsonify(game.to_dict()), 200
        else:
            return jsonify({"message": "Game not found"}), 404
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500


@app.route('/reviews', methods=['GET', 'POST'])
def reviews():
    if request.method == 'GET':
        try:
            reviews = [review.to_dict() for review in Review.query.all()]
            return jsonify(reviews), 200
        except SQLAlchemyError as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == 'POST':
        try:
            new_review = Review(
                score=request.form.get("score"),
                comment=request.form.get("comment"),
                game_id=request.form.get("game_id"),
                user_id=request.form.get("user_id"),
            )
            db.session.add(new_review)
            db.session.commit()
            return jsonify(new_review.to_dict()), 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500


@app.route('/reviews/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def review_by_id(id):
    try:
        review = Review.query.get(id)
        if not review:
            return jsonify({"message": "Review not found"}), 404

        if request.method == 'GET':
            return jsonify(review.to_dict()), 200

        elif request.method == 'PATCH':
            for attr in request.form:
                setattr(review, attr, request.form.get(attr))
            db.session.commit()
            return jsonify(review.to_dict()), 200

        elif request.method == 'DELETE':
            db.session.delete(review)
            db.session.commit()
            return jsonify({"delete_successful": True, "message": "Review deleted."}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route('/users')
def users():
    try:
        users = [user.to_dict() for user in User.query.all()]
        return jsonify(users), 200
    except SQLAlchemyError as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5555)
