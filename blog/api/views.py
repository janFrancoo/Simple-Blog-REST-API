from blog.api.models import Like, Post
from django.contrib.auth.models import User
from blog.api.serializers import LikeSerializer, UserSerializer, PostSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token

def confirm_token(func):
    def wrapper(request, *args, **kwargs):
        try:
            header_attr = request.META.get('HTTP_AUTHORIZATION', None)
            if header_attr is None:
                return Response({
                    "success": False,
                    "message": "Missing token"
                }, status=status.HTTP_400_BAD_REQUEST)
            token = header_attr.split(" ")[1]
            token_obj = Token.objects.get(key=token)
            request.user = token_obj.user
            if not args:
                return func(request)
            return func(request, args)
        except Token.DoesNotExist:
            return Response({
                "success": False,
                "message": "Invalid or missing token"
            }, status=status.HTTP_401_UNAUTHORIZED)
    return wrapper

def check_post_exists(func):
    def wrapper(request, pk):
        try:
            post = Post.objects.get(pk=pk)
            request.post = post
            return func(request, pk)
        except Post.DoesNotExist:
            return Response({
                "success": False,
                "message": "Post does not exists"
            }, status=status.HTTP_404_NOT_FOUND)
    return wrapper

def check_post_ownership(func):
    def wrapper(request, pk):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', None).split(" ")[1]
            token_obj = Token.objects.get(key=token)
            request.user = token_obj.user
            request.post = Post.objects.get(pk=pk)
            if request.user.username == request.post.author.username:
                return func(request, pk)
            else:
                return Response({
                    "success": False,
                    "message": "You not authorized to access this post"
                })
        except (Token.DoesNotExist, AttributeError):
            return Response({
                "success": False,
                "message": "Invalid or missing token"
            }, status=status.HTTP_401_UNAUTHORIZED)
        except Post.DoesNotExist:
            return Response({
                "success": False,
                "message": "Post does not exists"
            }, status=status.HTTP_404_NOT_FOUND)
    return wrapper

@api_view(['GET'])
def get_posts(request):
    posts = Post.objects.all()
    serializer_context = {
        'request': request,
    }
    serializer = PostSerializer(posts, many=True, context=serializer_context)
    return Response({
        "success": True,
        "data": serializer.data
    })

@api_view(['POST'])
@confirm_token
def add_post(request):
    request.data["author"] = request.user.pk
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "success": True,
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    return Response({
        "success": False,
        "message": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@check_post_exists
def get_single_post(request, pk):
    serializer = PostSerializer(request.post)
    return Response({
        "success": True,
        "data": serializer.data
    })

@api_view(['PUT'])
@check_post_ownership
def update_post(request, pk):
    request.data["author"] = request.user.pk
    serializer = PostSerializer(request.post, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "success": True,
            "data": serializer.data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@check_post_ownership
def delete_post(request, pk):
    post = request.post
    post.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@check_post_exists
@confirm_token
def like_post(request, pk):
    like = {
        "by": request.user.username,
        "post": pk[0]
    }
    serializer = LikeSerializer(data=like)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "success": True,
            "data": serializer.data
        })
    return Response({
        "success": False,
        "message": serializer.errors
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@check_post_exists
@confirm_token
def unlike_post(request, pk):
    try:
        like = Like.objects.get(by=request.user.username, post=pk[0])
        like.delete()
        return Response({
            "success": True,
        }, status=status.HTTP_204_NO_CONTENT)
    except Like.DoesNotExist:
        return Response({
            "success": False,
            "message": "No like entry"
        }, status=status.HTTP_404_NOT_FOUND)
