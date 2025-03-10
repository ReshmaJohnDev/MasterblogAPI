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

    # for GET request return the POST data
    sort_criteria = request.args.get('sort', None)
    sort_direction = request.args.get('direction', 'asc').lower()
    # Default to original posts if no sort parameters are given
    sorted_posts = POSTS

    # If a sort field is provided, proceed to sort
    if sort_criteria:
        # Check if the sort field is valid
        if sort_criteria not in ['title', 'content']:
            return jsonify({"error": "Invalid sort field. Use 'title' or 'content'."}), 400

        # Check if the sort direction is valid
        if sort_direction not in ['asc', 'desc']:
            return jsonify({"error": "Invalid direction. Use 'asc' or 'desc'."}), 400

        # Determine the reverse flag based on the direction
        reverse = True if sort_direction == 'desc' else False

        # Sort the posts based on the given field and direction
        sorted_posts = sorted(POSTS, key=lambda post: post[sort_criteria], reverse=reverse)

    paginated_posts = implement_pagination(sorted_posts)
    # Return the sorted or unsorted posts that's paginated
    return jsonify(paginated_posts)


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    # Find the post with the given ID
    post = find_post_by_id(id)

    # If the post wasn't found, return a 404 error
    if post is None:
        response = {
            "message": f"Post with id {id} was not found.",
        }
        return jsonify(response), 404

    #remove the post to delete from POSTS
    POSTS.remove(post)

    # Return a success message with the deleted post ID
    response = {
        "message": f"Post with id {id} has been deleted successfully.",
    }

    return jsonify(response), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    # Find the post with the given ID
    post = find_post_by_id(id)

    # If the post wasn't found, return a 404 error
    if post is None:
        response = {
            "message": f"Post with id {id} was not found.",
        }
        return jsonify(response), 404

    # Update the POSTS with the new data
    new_data = request.get_json()
    post.update(new_data)
    post['id'] = id

    # Return the updated POSTS
    return jsonify({"message": "Post updated successfully.", "post": post}), 200


@app.route('/api/posts/search')
def search_post():
    print("inside search")
    title = request.args.get('title', '').lower()
    content = request.args.get('content', '').lower()
    filtered_post = []

    # Loop through the posts and check if title or content matches
    for post in POSTS :
        title_match = (title and title in post['title'].lower())
        content_match = (content and content in post['content'].lower())
        if title_match or content_match:
            filtered_post.append(post)

    # If posts were found, return them
    if filtered_post:
        return jsonify(filtered_post)
    # If no posts match, return a response with a 404 status
    response = {
        "message": f"No posts match the search criteria",
        "post" : filtered_post
    }
    return jsonify(response), 404


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
