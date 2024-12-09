from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post, Comment, Like
import base64
import os
import json

class PostTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.post = Post.objects.create(author=self.author, text='Первоначальный пост')

    def test_create_post(self):
        with open('Design.png', 'rb') as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode('utf-8')

        response = self.client.post('/posts/', {
            'text': 'Новый пост',
            'image': f'data:image/jpeg;base64,{encoded_string}'
        })

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(Post.objects.last().text, 'Новый пост')
        last_post = Post.objects.last()
        self.assertIsNotNone(last_post.created_at)

    def test_edit_post_not_author(self):
        other_author = User.objects.create_user(username='otheruser', password='password')
        self.client.login(username='otheruser', password='password')

        image_path = os.path.join(os.path.dirname(__file__), '..', 'Design.png')

        with open(image_path, 'rb') as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode('utf-8')

        response = self.client.put(
            f'/posts/{self.post.id}/',
            json.dumps({
                'text': 'Попытка редактирования',
                'image': f'data:image/jpeg;base64,{encoded_string}'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 403)

    def test_edit_post(self):
        image_path = os.path.join(os.path.dirname(__file__), '..', 'Design.png')

        with open(image_path, 'rb') as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode('utf-8')

        response = self.client.put(f'/posts/{self.post.id}/', {
            'text': 'Отредактированный пост',
            'image': f'data:image/jpeg;base64,{encoded_string}'
        }, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, 'Отредактированный пост')

    def test_get_post_details(self):
        response = self.client.get(f'/posts/{self.post.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['text'], self.post.text)
        self.assertEqual(response.data['image'], self.post.image)
        self.assertEqual(response.data['comments_count'], self.post.comments.count())
        self.assertEqual(response.data['likes_count'], self.post.likes.count())


class CommentTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user(username='testuser', password='password')
        self.post = Post.objects.create(text='Новый прекрасный день', image='/posts/Design.png', author=self.author)

    def test_create_comment(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(f'/posts/{self.post.id}/comments/', {'text': 'Круто'})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.last().text, 'Круто')


        last_comment = Comment.objects.last()
        self.assertIsNotNone(last_comment.created_at)

    def test_create_comment_unauthorized(self):
        response = self.client.post(f'/posts/{self.post.id}/comments/', {'text': 'Круто'})
        self.assertEqual(response.status_code, 401)

    def test_get_post_details_with_comments(self):
        self.client.login(username='testuser', password='password')
        self.client.post(f'/posts/{self.post.id}/comments/', {'text': 'Круто'})
        response = self.client.get(f'/posts/{self.post.id}/')
        self.assertIn('comments', response.data)
        self.assertEqual(len(response.data['comments']), 1)
        self.assertEqual(response.data['comments'][0]['text'], 'Круто')


class LikePostTests(TestCase):

    def setUp(self):
        self.author = User.objects.create_user(username='testuser', password='password')
        self.post = Post.objects.create(text='Новый прекрасный день', image='/posts/Design.png', author=self.author)

    def test_like_post(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(f'/posts/{self.post.id}/likes/', data={'post': self.post.id})
        self.assertEqual(response.status_code, 201)

    def test_like_post_unauthorized(self):
        response = self.client.post(f'/posts/{self.post.id}/likes/')
        self.assertEqual(response.status_code, 401)

    def test_unlike_post(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(f'/posts/{self.post.id}/likes/', data={'post': self.post.id})
        self.assertEqual(response.status_code, 201)
        like_id = response.data['id']
        response = self.client.delete(f'/posts/{self.post.id}/likes/{like_id}/')
        self.assertEqual(response.status_code, 204)
