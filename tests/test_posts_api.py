import pytest
from rest_framework.test import APIClient
from apps.users.models import User
from apps.posts.models import Post

pytestmark = pytest.mark.django_db

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(email="u1@example.com", password="pass123")

@pytest.fixture
def other_user():
    return User.objects.create_user(email="u2@example.com", password="pass123")

def test_list_posts_anon_ok(client, user):
    Post.objects.create(user=user, title="t1", text="hello")
    Post.objects.create(user=user, title="t2", text="world")
    url = "/api/posts/"
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.data["count"] == 2

def test_create_requires_auth(client):
    resp = client.post("/api/posts/", {"title": "x", "text": "y"}, format="multipart")
    assert resp.status_code in (401, 403)

def test_create_as_user_ok(client, user):
    client.login(email=user.email, password="pass123")
    resp = client.post("/api/posts/", {"title": "x", "text": "y"}, format="multipart")
    assert resp.status_code == 201
    assert resp.data["user"] == user.id

def test_update_only_author(client, user, other_user):
    post = Post.objects.create(user=user, title="t", text="z")
    client.login(email=other_user.email, password="pass123")
    resp = client.patch(f"/api/posts/{post.id}/", {"title": "nope"})
    assert resp.status_code in (403, 404)

    client.logout()
    client.login(email=user.email, password="pass123")
    resp = client.patch(f"/api/posts/{post.id}/", {"title": "ok"})
    assert resp.status_code == 200
    assert resp.data["title"] == "ok"
