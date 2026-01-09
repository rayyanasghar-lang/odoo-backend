from odoo import http
from odoo.http import request

class BlogController(http.Controller):

    @http.route(['/blog', '/blog/page/<int:page>'], type='http', auth='public', website=True)
    def blog_list(self, page=1, **kw):
        domain = [('published', '=', True)]
        category_id = kw.get('category_id')
        if category_id:
            try:
                cid = int(category_id)
                domain = domain + [('category_id', '=', cid)]
            except Exception:
                pass
        posts = request.env['blog.post'].sudo().search(domain, order='date desc')
        categories = request.env['blog.category'].sudo().search([])
        return request.render('blog_api.blog_list_template', {
            'posts': posts,
            'categories': categories,
            'selected_category': int(category_id) if category_id else False
        })

    @http.route(['/blog/<model("blog.post"):post>'], type='http', auth='public', website=True)
    def blog_detail(self, post, **kw):
        post = post.sudo()
        categories = request.env['blog.category'].sudo().search([])
        return request.render('blog_api.blog_detail_template', {
            'post': post,
            'categories': categories,
        })

    @http.route(['/blog/category/<int:category_id>'], type='http', auth='public', website=True)
    def blog_category(self, category_id=0, **kw):
        return http.redirect_with_hash('/blog?category_id=%s' % (category_id,))

    @http.route(['/api/blog/posts'], type='json', auth='public', methods=['POST'], csrf=False)
    def api_blog_posts_list(self, **kwargs):
        """Get all published blog posts"""
        try:
            domain = [('published', '=', True)]
            posts = request.env['blog.post'].sudo().search_read(
                domain, 
                ['id', 'title', 'slug', 'content', 'date', 'category_id', 'author_name', 'published']
            )
            return {'success': True, 'data': posts, 'count': len(posts)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route(['/api/blog/posts/<int:post_id>'], type='json', auth='public', methods=['POST'], csrf=False)
    def api_blog_post_detail(self, post_id, **kwargs):
        """Get a single blog post by ID"""
        try:
            post = request.env['blog.post'].sudo().search_read(
                [('id', '=', post_id)],
                ['id', 'title', 'slug', 'content', 'date', 'category_id', 'author_name', 'published']
            )
            if post:
                return {'success': True, 'data': post[0]}
            else:
                return {'success': False, 'error': 'Post not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route(['/api/blog/posts/create'], type='json', auth='user', methods=['POST'], csrf=False)
    def api_blog_post_create(self, **kwargs):
        """Create a new blog post"""
        try:
            # Get data from request
            title = kwargs.get('title')
            content = kwargs.get('content', '')
            category_id = kwargs.get('category_id')
            author_name = kwargs.get('author_name', request.env.user.name)
            published = kwargs.get('published', False)

            # Validate required fields
            if not title:
                return {'success': False, 'error': 'Title is required'}

            # Create the post
            post = request.env['blog.post'].sudo().create({
                'title': title,
                'content': content,
                'category_id': category_id,
                'author_name': author_name,
                'published': published,
            })

            return {
                'success': True,
                'message': 'Post created successfully',
                'data': {
                    'id': post.id,
                    'title': post.title,
                    'slug': post.slug,
                    'date': str(post.date),
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route(['/api/blog/posts/<int:post_id>/update'], type='json', auth='user', methods=['POST'], csrf=False)
    def api_blog_post_update(self, post_id, **kwargs):
        """Update an existing blog post"""
        try:
            post = request.env['blog.post'].sudo().browse(post_id)
            
            if not post.exists():
                return {'success': False, 'error': 'Post not found'}

            # Prepare update data
            update_data = {}
            if 'title' in kwargs:
                update_data['title'] = kwargs['title']
            if 'content' in kwargs:
                update_data['content'] = kwargs['content']
            if 'category_id' in kwargs:
                update_data['category_id'] = kwargs['category_id']
            if 'author_name' in kwargs:
                update_data['author_name'] = kwargs['author_name']
            if 'published' in kwargs:
                update_data['published'] = kwargs['published']

            # Update the post
            post.write(update_data)

            return {
                'success': True,
                'message': 'Post updated successfully',
                'data': {
                    'id': post.id,
                    'title': post.title,
                    'slug': post.slug,
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route(['/api/blog/posts/<int:post_id>/delete'], type='json', auth='user', methods=['POST'], csrf=False)
    def api_blog_post_delete(self, post_id, **kwargs):
        """Delete a blog post"""
        try:
            post = request.env['blog.post'].sudo().browse(post_id)
            
            if not post.exists():
                return {'success': False, 'error': 'Post not found'}

            post.unlink()

            return {
                'success': True,
                'message': 'Post deleted successfully',
                'data': {'id': post_id}
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route(['/api/blog/categories'], type='json', auth='public', methods=['POST'], csrf=False)
    def api_blog_categories(self, **kwargs):
        """Get all blog categories"""
        try:
            categories = request.env['blog.category'].sudo().search_read(
                [],
                ['id', 'name']
            )
            return {'success': True, 'data': categories, 'count': len(categories)}
        except Exception as e:
            return {'success': False, 'error': str(e)}

