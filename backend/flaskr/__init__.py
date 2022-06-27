import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"*": {"origins": '*'}})

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers', 'Content-Type,Authorization,true'
        )
        response.headers.add(
            'Access-Control-Allow-Methods', 'GET,POST,PATCH,PUT,DELETE,OPTIONS'
        ) 
        return response

   
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        all_categories = {}
        for category in categories:
            all_categories[category.id] = category.type

        if len(categories) == 0:
            abort(404)
        
        return jsonify({
            'success': True,
            'categories': all_categories,
            'total': len(categories) 
        })  
   

    @app.route('/questions')
    def get_questions():       
        try:
            selection = Question.query.order_by(Question.id).all()
            total = Question.query.count()        
            current_questions = paginate_questions(request, selection)      
            categories = Category.query.all()
            all_categories = {}

            if len(current_questions) == 0:
                abort(404)
            for category in categories:
                all_categories[category.id] = category.type                   
             

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': total,
                'categories': all_categories,            
                'current_category': 'History'            
        }) 
        except:
            print(sys.exc_info())
            abort(400)       


    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            print(question)

            if question == None:
                abort(404)
            question.delete()  

            return jsonify({
                'question_id': question.id,
                'success': True
            }), 200

        except:
            print(sys.exc_info())
            abort(422)   

    
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)

        try:

            question = Question(
                question=new_question, 
                answer=new_answer, 
                category=new_category, 
                difficulty=new_difficulty
            )
            question.insert()

            return jsonify({
                'question': new_question,
                'answer': new_answer,
                'difficulty': new_difficulty,
                'category': new_category,
                'success': True
            })
        except:            
            print(sys.exc_info())
            abort(422)    

   
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)
        formatted_search_term = f'%{search_term}%'
        questions = Question.query.filter(
            Question.question.ilike(formatted_search_term)
        )
        if search_term:
            searched_questions = questions.all()
            total = questions.count()
            paginated_questions = paginate_questions(request, searched_questions)

        
            return jsonify({
                'questions': paginated_questions,
                'total_questions': total,
                'current_category': 'Entertainment',
                'success': True
            })
        else:            
            print(sys.exc_info())
            abort(404)        


   
    @app.route('/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        category = Category.query.get(category_id)
        questions = Question.query.order_by(Question.id).all()
        question_list = []
        try:
            for question in questions:
                if question.category == category.id:
                    question_list.append(question)
            total = len(question_list)        
            paginated_questions = paginate_questions(request, question_list)

            return jsonify({
                'question': paginated_questions,
                'total_questions': total,
                'success': True,
                'current_category': category.type
            })       
        except:            
            print(sys.exc_info())
            abort(404)     

   
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        body = request.get_json()
        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')
        print(previous_questions)
        print(quiz_category)
        category = Category.query.filter(
            Category.id == quiz_category['id']
            ).first()        
        questions = Question.query.order_by(Question.id).all()           
        new_question_list = []
        try:
            if quiz_category['id'] == 0:
                question_list = [question.format() for question in questions]
                new_quiz_question = random.choice(question_list) 
                
            else:
                for question in questions:
                    if question.category == category.id:
                        new_question_list.append(question)
                question_list = [question.format() for question in new_question_list] 
            
            new_quiz_question = random.choice(question_list)
            while new_quiz_question['id'] not in previous_questions:
                return jsonify({
                    'question': new_quiz_question,
                    'success': True                
                })
        except:
            print(sys.exc_info())
            abort(404)


    ### Error Handlers
    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify ({
                "message": "bad request",
                "success": False,
                "error": 400
            }), 400
        )

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({
            "message": "resource not found",
            "success": False,
            "error": 404
            }), 404
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({
                "message": "unprocessable",
                "success": False,
                "error": 422
            }), 422
        )

    
    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({
                "success": False,
                "error": 405,
                "message": "method not allowed"
            }), 405
        )

    @app.errorhandler(500)
    def server_error(error):
        return (
            jsonify({
                "message": "server error",
                "success": False,
                "error": 500
            }), 500
        )         
        
    return app

