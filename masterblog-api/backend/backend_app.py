import logging
from flask import Flask, jsonify , request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
limiter = Limiter(app=app, key_func=get_remote_address)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


POSTS = [
    {"id": 1, "title": "First post1", "content": "This is the first post."},
    {"id": 2, "title": "Second post1", "content": "This is the second post."},
]

def validate_post_data(data):
  if "title" not in data or "content" not in data:
    return False
  return True


def find_post_by_id(post_id):
    """ Find the post with the id `post_id`.
    If there is no post with this id, return None. """
    post = next((post for post in POSTS if post['id'] == post_id) ,None)
    if post is None:
      return None
    return  post

def implement_pagination(posts):
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    start_index = (page - 1) * limit
    end_index = start_index + limit
    return posts[start_index:end_index]


@app.route('/api/posts', methods=['GET', 'POST'])
@limiter.limit("10/minute") # Limit to 10 requests per minute
def get_posts():
    if request.method == 'POST':
        # Get the new post data from the client
        new_post = request.get_json()
        if not validate_post_data(new_post):
            return jsonify({"error": "Invalid POST data , 'title' and 'content' fields are mandatory"}), 400

        # Generate a new ID for the post
        new_id = max(post['id'] for post in POSTS) + 1
        new_post['id'] = new_id

        # Add the new post to our list
        POSTS.append(new_post)
        response = {
            "message": f" New post with id {new_id} has been added successfully.",
            "posts": new_post
        }
        # Return the new post data to the client
        return jsonify(response), 201
    return jsonify(POSTS)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
