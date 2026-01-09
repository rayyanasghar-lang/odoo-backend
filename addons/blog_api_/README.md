# Blog API

A comprehensive blog module for Odoo 19 with posts, categories, and website integration.

## Features

- ✨ **Blog Post Management**: Create, edit, and manage blog posts with rich content
- 📁 **Categories**: Organize posts with categories for better navigation
- 🌐 **Website Integration**: Public-facing blog pages with responsive design
- 🔌 **RESTful API**: HTTP endpoints for external blog management
- 👤 **Author Management**: Track post authors and metadata
- 🎨 **Clean Templates**: Modern, responsive blog templates

## Installation

1. Copy the `blog_api` folder to your Odoo addons directory
2. Update the addons list in Odoo
3. Install the module from Apps menu

## Configuration

No additional configuration required. The module works out of the box.

## Usage

### Backend Usage

1. Navigate to **Website > Blog > Posts** to manage blog posts
2. Navigate to **Website > Blog > Categories** to manage categories
3. Create new posts and assign them to categories

### Frontend Usage

Visit `/blog` on your website to see the public blog listing.

### API Endpoints

The module provides the following API endpoints:

- `GET /api/blog/posts` - List all blog posts
- `GET /api/blog/posts/<int:post_id>` - Get a specific post
- `POST /api/blog/posts` - Create a new post
- `PUT /api/blog/posts/<int:post_id>` - Update a post
- `DELETE /api/blog/posts/<int:post_id>` - Delete a post

## Requirements

- Odoo 19.0
- Website module

## License

LGPL-3

## Author

Your Name

## Support

For issues and questions, please visit: https://github.com/yourusername/blog_api/issues
