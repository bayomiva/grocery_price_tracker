import os
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import GroceryItem
from .serializers import GroceryItemSerializer

ALLOWED_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}


class ItemListView(generics.ListAPIView):
    serializer_class = GroceryItemSerializer
    permission_classes = [permissions.AllowAny]
    queryset = GroceryItem.objects.all()


class ItemDetailView(generics.RetrieveUpdateAPIView):
    """GET /api/items/<pk>/  —  PATCH /api/items/<pk>/  (staff only for writes)."""
    queryset = GroceryItem.objects.all()
    serializer_class = GroceryItemSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class ItemImageUploadView(APIView):
    """POST /api/items/<pk>/upload-image/  — multipart file upload (staff only)."""
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        item = get_object_or_404(GroceryItem, pk=pk)
        img = request.FILES.get('image')
        if not img:
            return Response({'detail': 'No image file provided.'}, status=400)

        ext = os.path.splitext(img.name)[1].lower()
        if ext not in ALLOWED_EXTS:
            return Response(
                {'detail': f'Unsupported format. Allowed: {", ".join(sorted(ALLOWED_EXTS))}'},
                status=400,
            )

        # Save to media/items/<pk><ext>, overwrite any previous upload
        rel_path = f'items/{pk}{ext}'
        if default_storage.exists(rel_path):
            default_storage.delete(rel_path)
        default_storage.save(rel_path, ContentFile(img.read()))

        # Store a root-relative path — NOT an absolute URL.
        # Absolute URLs (request.build_absolute_uri) bake in the current hostname,
        # which breaks when accessed from a different host (other users, production
        # domain, redeployment). A root-relative path always resolves correctly.
        item.image_url = f'/media/{rel_path}'
        item.save(update_fields=['image_url'])
        return Response({'id': item.id, 'image_url': item.image_url})
