from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from .models import Comment
from .serializer import CommentCreateSerializer, CommentListSerializer, CommentDetailSerializer
from ad.models import Ad
from user.models import Profile, Role
from .services import update_performer_rating

User = get_user_model()


class CommentListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentListSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentListSerializer

    def get_queryset(self):
        ad_id = self.request.query_params.get('ad')
        if ad_id:
            ad = get_object_or_404(Ad, id=ad_id)
            return Comment.objects.filter(ad=ad).order_by('-created_at')
        return Comment.objects.none()

    def perform_create(self, serializer):
        ad = serializer.validated_data['ad']
        if ad.creator != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the ad creator can rate the performer.")

        if ad.status != Ad.Status.DONE:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("Can only rate performers for completed ads.")
        
        performer = serializer.validated_data['performer']
        if ad.performer != performer:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("The performer being rated is not the one assigned to this ad.")

        existing_comment = Comment.objects.filter(ad=ad).first()
        if existing_comment:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("A rating already exists for this ad.")

        comment = serializer.save(user=self.request.user)

        performer = ad.performer
        if performer:
            update_performer_rating(performer, comment.rating)
            

class CommentDetailAPIView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentDetailSerializer
    queryset = Comment.objects.all()


class PerformerRatingListView(ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = None  
    def get_serializer_class(self):
        from rest_framework import serializers

        class PerformerRatingSerializer(serializers.ModelSerializer):
            avg_rating = serializers.FloatField(read_only=True)
            comment_count = serializers.IntegerField(read_only=True)
            profile_id = serializers.IntegerField(source='profile.id', read_only=True)

            class Meta:
                model = User
                fields = ['id', 'username', 'first_name', 'last_name', 'avg_rating', 'comment_count', 'profile_id']

        return PerformerRatingSerializer

    def get_queryset(self):
        performer_role = Role.objects.get(name=Role.Names.PERFORMER)
        performers = User.objects.filter(roles=performer_role)

        performers = performers.annotate(
            avg_rating=Avg('ads_performed__comments__rating'),
            comment_count=Count('ads_performed__comments')
        ).filter(
            avg_rating__isnull=False  
        )

        # Apply filters
        min_rating = self.request.query_params.get('min_rating')
        max_rating = self.request.query_params.get('max_rating')
        min_comments = self.request.query_params.get('min_comments')
        max_comments = self.request.query_params.get('max_comments')

        if min_rating:
            performers = performers.filter(avg_rating__gte=min_rating)
        if max_rating:
            performers = performers.filter(avg_rating__lte=max_rating)
        if min_comments:
            performers = performers.filter(comment_count__gte=min_comments)
        if max_comments:
            performers = performers.filter(comment_count__lte=max_comments)

        # Sort by parameters
        sort_by = self.request.query_params.get('sort_by', 'avg_rating')  # Default sort by rating
        order = self.request.query_params.get('order', 'desc')  # Default descending

        if order == 'asc':
            performers = performers.order_by(sort_by)
        else:
            performers = performers.order_by(f'-{sort_by}')

        return performers