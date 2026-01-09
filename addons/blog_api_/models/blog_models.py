from odoo import models, fields, api
from odoo.tools import misc


class BlogCategory(models.Model):
    _name = 'blog.category'
    _description = 'Blog Category'
    _order = 'name asc'

    name = fields.Char(string='Name', required=True)
    post_ids = fields.One2many('blog.post', 'category_id', string='Posts')

class BlogPost(models.Model):
    _name = 'blog.post'
    _description = 'Blog Post'
    _order = 'date desc'

    title = fields.Char(string='Title', required=True)
    slug = fields.Char(string='Slug', index=True)
    content = fields.Html(string='Content')
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    published = fields.Boolean(string='Published', default=False)
    category_id = fields.Many2one('blog.category', string='Category')
    author_name = fields.Char(string='Author')

    @api.model
    def create(self, vals):
        if vals.get('title') and not vals.get('slug'):
            vals['slug'] = misc.slugify(vals.get('title'))
        return super().create(vals)

    def write(self, vals):
        if 'title' in vals and not vals.get('slug'):
            vals['slug'] = misc.slugify(vals.get('title'))
        return super().write(vals)

    def name_get(self):
        result = []
        for rec in self:
            name = rec.title or '/'

            result.append((rec.id, name))
        return result
