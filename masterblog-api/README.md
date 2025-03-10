# Masterblog API

This is a simple Flask API for managing blog posts with features such as creation, deletion, update, searching, pagination, and sorting. The API also includes rate limiting and handles errors gracefully.

## Features
- **Create Posts**: Add new posts with a title and content.
- **Read Posts**: Fetch all posts with support for sorting and pagination.
- **Update Posts**: Modify existing posts based on post ID.
- **Delete Posts**: Delete a post by its ID.
- **Search Posts**: Search posts by title or content.
- **Rate Limiting**: Limits the number of requests to 10 per minute.
- **Error Handling**: Custom error handlers for 404 and 405 errors.

## Prerequisites
Before running this application, make sure you have the following installed:

- Python 3.x
- `pip` (Python's package manager)

You will also need to install the following Python libraries:
- Flask
- Flask-CORS
- Flask-Limiter

You can install the required dependencies with:

```bash
pip install -r requirements.txt
