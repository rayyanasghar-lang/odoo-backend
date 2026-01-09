# Blog API - Frontend Developer Documentation

> [!IMPORTANT]
> This documentation is designed for frontend developers building a Next.js application with shadcn/ui components to consume the Odoo Blog API.

## Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Data Models](#data-models)
- [API Endpoints](#api-endpoints)
- [Next.js Integration](#nextjs-integration)
- [shadcn/ui Components](#shadcnui-components)
- [Error Handling](#error-handling)
- [Example Implementation](#example-implementation)

---

## Overview

The Blog API provides a RESTful interface for managing blog posts and categories. All API endpoints return JSON responses with a consistent structure.

### Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "data": { /* response data */ },
  "count": 10,  // Optional: for list endpoints
  "message": "Operation successful",  // Optional: for create/update/delete
  "error": "Error message"  // Only present when success is false
}
```

---

## Base URL

```
http://your-odoo-domain.com
```

> [!NOTE]
> Replace `your-odoo-domain.com` with your actual Odoo instance URL.

---

## Authentication

### Public Endpoints (No Authentication Required)
- `GET /api/blog/posts` - List all posts
- `GET /api/blog/posts/<post_id>` - Get single post
- `GET /api/blog/categories` - List all categories

### Authenticated Endpoints (Requires Login)
- `POST /api/blog/posts/create` - Create post
- `POST /api/blog/posts/<post_id>/update` - Update post
- `POST /api/blog/posts/<post_id>/delete` - Delete post

> [!WARNING]
> All authenticated endpoints require `auth='user'`. You'll need to implement session-based authentication with your Odoo backend.

---

## Data Models

### BlogPost

```typescript
interface BlogPost {
  id: number;
  title: string;
  slug: string;
  content: string;  // HTML content
  date: string;     // ISO 8601 datetime string
  category_id: [number, string] | false;  // [id, name] or false
  author_name: string;
  published: boolean;
}
```

### BlogCategory

```typescript
interface BlogCategory {
  id: number;
  name: string;
}
```

### API Response Types

```typescript
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  count?: number;
  message?: string;
  error?: string;
}
```

---

## API Endpoints

### 1. List All Blog Posts

**Endpoint:** `POST /api/blog/posts`

**Method:** `POST` (JSON-RPC style)

**Authentication:** Public

**Description:** Retrieves all published blog posts.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {}
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "My First Blog Post",
      "slug": "my-first-blog-post",
      "content": "<p>This is the content...</p>",
      "date": "2025-11-25 16:30:00",
      "category_id": [1, "Technology"],
      "author_name": "John Doe",
      "published": true
    }
  ],
  "count": 1
}
```

---

### 2. Get Single Blog Post

**Endpoint:** `POST /api/blog/posts/<post_id>`

**Method:** `POST` (JSON-RPC style)

**Authentication:** Public

**Description:** Retrieves a specific blog post by ID.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {}
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "My First Blog Post",
    "slug": "my-first-blog-post",
    "content": "<p>This is the content...</p>",
    "date": "2025-11-25 16:30:00",
    "category_id": [1, "Technology"],
    "author_name": "John Doe",
    "published": true
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Post not found"
}
```

---

### 3. Create Blog Post

**Endpoint:** `POST /api/blog/posts/create`

**Method:** `POST` (JSON-RPC style)

**Authentication:** Required (user must be logged in)

**Description:** Creates a new blog post.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "title": "New Blog Post",
    "content": "<p>Post content here...</p>",
    "category_id": 1,
    "author_name": "Jane Smith",
    "published": false
  }
}
```

**Required Fields:**
- `title` (string)

**Optional Fields:**
- `content` (string, HTML)
- `category_id` (integer)
- `author_name` (string, defaults to current user's name)
- `published` (boolean, defaults to false)

**Response:**
```json
{
  "success": true,
  "message": "Post created successfully",
  "data": {
    "id": 2,
    "title": "New Blog Post",
    "slug": "new-blog-post",
    "date": "2025-11-25 16:35:00"
  }
}
```

---

### 4. Update Blog Post

**Endpoint:** `POST /api/blog/posts/<post_id>/update`

**Method:** `POST` (JSON-RPC style)

**Authentication:** Required (user must be logged in)

**Description:** Updates an existing blog post.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "title": "Updated Title",
    "content": "<p>Updated content...</p>",
    "published": true
  }
}
```

**Updatable Fields:**
- `title` (string)
- `content` (string, HTML)
- `category_id` (integer)
- `author_name` (string)
- `published` (boolean)

> [!NOTE]
> Only include fields you want to update. Omitted fields will remain unchanged.

**Response:**
```json
{
  "success": true,
  "message": "Post updated successfully",
  "data": {
    "id": 2,
    "title": "Updated Title",
    "slug": "updated-title"
  }
}
```

---

### 5. Delete Blog Post

**Endpoint:** `POST /api/blog/posts/<post_id>/delete`

**Method:** `POST` (JSON-RPC style)

**Authentication:** Required (user must be logged in)

**Description:** Deletes a blog post.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {}
}
```

**Response:**
```json
{
  "success": true,
  "message": "Post deleted successfully",
  "data": {
    "id": 2
  }
}
```

---

### 6. List All Categories

**Endpoint:** `POST /api/blog/categories`

**Method:** `POST` (JSON-RPC style)

**Authentication:** Public

**Description:** Retrieves all blog categories.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {}
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Technology"
    },
    {
      "id": 2,
      "name": "Lifestyle"
    }
  ],
  "count": 2
}
```

---

## Next.js Integration

### Project Setup

#### 1. Initialize Next.js Project

```bash
npx create-next-app@latest blog-frontend
cd blog-frontend
```

**Recommended Options:**
- TypeScript: Yes
- ESLint: Yes
- Tailwind CSS: Yes
- App Router: Yes
- Import alias: Yes (@/*)

#### 2. Install shadcn/ui

```bash
npx shadcn-ui@latest init
```

**Configuration:**
- Style: Default
- Base color: Slate
- CSS variables: Yes

#### 3. Install Required Components

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add select
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add form
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add skeleton
```

---

### API Service Layer

Create a service to handle API calls:

**`lib/api/blog.ts`**

```typescript
const BASE_URL = process.env.NEXT_PUBLIC_ODOO_URL || 'http://localhost:8069';

interface JsonRpcRequest {
  jsonrpc: string;
  method: string;
  params: any;
  id?: number;
}

async function jsonRpcCall(endpoint: string, params: any = {}) {
  const payload: JsonRpcRequest = {
    jsonrpc: '2.0',
    method: 'call',
    params,
    id: Math.floor(Math.random() * 1000000),
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // Important for session cookies
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data.result;
}

export const blogApi = {
  // Get all posts
  async getPosts() {
    return jsonRpcCall('/api/blog/posts');
  },

  // Get single post
  async getPost(postId: number) {
    return jsonRpcCall(`/api/blog/posts/${postId}`);
  },

  // Create post (requires authentication)
  async createPost(postData: {
    title: string;
    content?: string;
    category_id?: number;
    author_name?: string;
    published?: boolean;
  }) {
    return jsonRpcCall('/api/blog/posts/create', postData);
  },

  // Update post (requires authentication)
  async updatePost(postId: number, postData: Partial<{
    title: string;
    content: string;
    category_id: number;
    author_name: string;
    published: boolean;
  }>) {
    return jsonRpcCall(`/api/blog/posts/${postId}/update`, postData);
  },

  // Delete post (requires authentication)
  async deletePost(postId: number) {
    return jsonRpcCall(`/api/blog/posts/${postId}/delete`);
  },

  // Get all categories
  async getCategories() {
    return jsonRpcCall('/api/blog/categories');
  },
};
```

---

### Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_ODOO_URL=http://localhost:8069
```

---

## shadcn/ui Components

### Recommended Components for Blog UI

#### 1. Blog Post Card

Use `Card` component to display blog posts in a grid/list:

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export function BlogPostCard({ post }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{post.title}</CardTitle>
        <CardDescription>
          {post.author_name} • {new Date(post.date).toLocaleDateString()}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div dangerouslySetInnerHTML={{ __html: post.content.substring(0, 200) + '...' }} />
        {post.category_id && (
          <Badge variant="secondary">{post.category_id[1]}</Badge>
        )}
      </CardContent>
    </Card>
  );
}
```

#### 2. Blog Post Form

Use `Form`, `Input`, `Textarea`, and `Select` for creating/editing posts:

```tsx
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export function BlogPostForm({ onSubmit, categories }) {
  return (
    <form onSubmit={onSubmit}>
      <Input name="title" placeholder="Post Title" required />
      <Textarea name="content" placeholder="Post Content" />
      <Select name="category_id">
        <SelectTrigger>
          <SelectValue placeholder="Select Category" />
        </SelectTrigger>
        <SelectContent>
          {categories.map(cat => (
            <SelectItem key={cat.id} value={cat.id.toString()}>
              {cat.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      <Button type="submit">Create Post</Button>
    </form>
  );
}
```

#### 3. Loading States

Use `Skeleton` for loading states:

```tsx
import { Skeleton } from '@/components/ui/skeleton';

export function BlogPostSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-3/4" />
      <Skeleton className="h-4 w-1/2" />
      <Skeleton className="h-32 w-full" />
    </div>
  );
}
```

---

## Error Handling

### Client-Side Error Handling

```typescript
import { toast } from '@/components/ui/use-toast';

async function handleApiCall() {
  try {
    const result = await blogApi.getPosts();
    
    if (!result.success) {
      toast({
        title: 'Error',
        description: result.error || 'Something went wrong',
        variant: 'destructive',
      });
      return;
    }
    
    // Handle success
    return result.data;
  } catch (error) {
    toast({
      title: 'Network Error',
      description: 'Failed to connect to the server',
      variant: 'destructive',
    });
  }
}
```

---

## Example Implementation

### Blog Posts List Page

**`app/blog/page.tsx`**

```tsx
'use client';

import { useEffect, useState } from 'react';
import { blogApi } from '@/lib/api/blog';
import { BlogPostCard } from '@/components/blog-post-card';
import { BlogPostSkeleton } from '@/components/blog-post-skeleton';
import { toast } from '@/components/ui/use-toast';

export default function BlogPage() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPosts() {
      try {
        const result = await blogApi.getPosts();
        
        if (result.success) {
          setPosts(result.data);
        } else {
          toast({
            title: 'Error',
            description: result.error,
            variant: 'destructive',
          });
        }
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to load posts',
          variant: 'destructive',
        });
      } finally {
        setLoading(false);
      }
    }

    fetchPosts();
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map(i => <BlogPostSkeleton key={i} />)}
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-4xl font-bold mb-8">Blog Posts</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {posts.map(post => (
          <BlogPostCard key={post.id} post={post} />
        ))}
      </div>
    </div>
  );
}
```

---

## Additional Notes

### CORS Configuration

> [!WARNING]
> You may need to configure CORS on your Odoo instance to allow requests from your Next.js frontend.

### HTML Content Sanitization

> [!CAUTION]
> The `content` field contains HTML. Always sanitize HTML before rendering to prevent XSS attacks. Consider using a library like `DOMPurify`.

```bash
npm install dompurify
npm install --save-dev @types/dompurify
```

```tsx
import DOMPurify from 'dompurify';

function SafeHtmlContent({ html }) {
  const sanitized = DOMPurify.sanitize(html);
  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
}
```

### Date Formatting

Use a library like `date-fns` for better date formatting:

```bash
npm install date-fns
```

```tsx
import { format } from 'date-fns';

const formattedDate = format(new Date(post.date), 'PPP');
```

---

## Quick Start Checklist

- [ ] Initialize Next.js project with TypeScript
- [ ] Install and configure shadcn/ui
- [ ] Install required shadcn components (card, button, form, etc.)
- [ ] Create API service layer (`lib/api/blog.ts`)
- [ ] Set up environment variables (`.env.local`)
- [ ] Install additional dependencies (DOMPurify, date-fns)
- [ ] Create reusable components (BlogPostCard, BlogPostForm, etc.)
- [ ] Implement blog listing page
- [ ] Implement blog detail page
- [ ] Implement create/edit forms (for authenticated users)
- [ ] Add error handling and loading states
- [ ] Configure CORS on Odoo backend

---

## Support

For backend API issues, refer to the main [README.md](./README.md) or contact the backend team.

For Next.js or shadcn/ui questions, refer to:
- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com)
